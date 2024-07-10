from __future__ import annotations

import json
import logging
import subprocess
from collections import Counter, defaultdict
from copy import copy
from datetime import datetime
from fnmatch import fnmatch
from functools import cached_property
from pathlib import Path
from typing import DefaultDict, Dict, List, Optional, Union
from urllib.parse import urljoin, urlsplit

import requests

from ingest_validation_tools.enums import OtherTypes, Sample
from ingest_validation_tools.error_report import ErrorDict, ErrorDictException, InfoDict
from ingest_validation_tools.plugin_validator import (
    ValidatorError as PluginValidatorError,
)
from ingest_validation_tools.plugin_validator import run_plugin_validators_iter
from ingest_validation_tools.schema_loader import (
    AncestorTypeInfo,
    EntityTypeInfo,
    PreflightError,
    SchemaVersion,
    get_table_schema,
)
from ingest_validation_tools.table_validator import ReportType, get_table_errors
from ingest_validation_tools.validation_utils import (
    cedar_api_call,
    get_data_dir_errors,
    get_entity_api_data,
    get_entity_type_vals,
    get_json,
    get_schema_version,
    read_rows,
)

TSV_SUFFIX = "metadata.tsv"
CONSTRAINTS_CHECK_METHOD = "ancestors"


class Upload:
    def __init__(
        self,
        directory_path: Path,
        tsv_paths: list = [],
        optional_fields: list = [],
        add_notes: bool = True,
        dataset_ignore_globs: list = [],
        upload_ignore_globs: list = [],
        plugin_directory: Union[Path, None] = None,
        encoding: str = "utf-8",
        no_url_checks: bool = False,
        ignore_deprecation: bool = False,
        extra_parameters: Union[dict, None] = None,
        globus_token: str = "",
        run_plugins: bool = True,
        app_context: dict = {},
        verbose: bool = True,
        report_type: ReportType = ReportType.STR,
    ):
        self.directory_path = directory_path
        self.optional_fields = optional_fields
        self.dataset_ignore_globs = dataset_ignore_globs
        self.upload_ignore_globs = upload_ignore_globs
        self.plugin_directory = plugin_directory
        self.encoding = encoding
        self.no_url_checks = no_url_checks
        self.add_notes = add_notes
        self.ignore_deprecation = ignore_deprecation
        self.extra_parameters = extra_parameters if extra_parameters else {}
        self.effective_tsv_paths = {}
        self.globus_token = globus_token
        self.run_plugins = run_plugins
        self.verbose = verbose
        self.report_type = report_type

        self.check_fields = [
            "parent_sample_id",
            "source_id",
            "sample_id",
        ]
        self.errors = ErrorDict()
        self.info = InfoDict()

        self.get_app_context(app_context)

        try:
            self._get_effective_tsvs(tsv_paths)
            self._check_multi_assay()
            if not self.is_multi_assay:
                self._check_single_assay()

            self.is_shared_upload = {"global", "non_global"} == {
                x
                for x in self.directory_path.glob("*global")
                if x.is_dir() and x.name in ["global", "non_global"]
            }

        except PreflightError as e:
            self.errors.preflight = str(e)

    #####################
    #
    # Public methods:
    #
    #####################

    def get_info(self) -> InfoDict:
        """
        If called before get_errors, will report dir schema major version only.
        TODO: create a method that calls get_errors and then get_info as a unified
        way of retrieving all necessary info about the upload
        """
        self.info.time = datetime.now()
        self.info.dir = str(self.directory_path)

        git_version = subprocess.check_output(
            "git rev-parse --short HEAD".split(" "),
            encoding="ascii",
            stderr=subprocess.STDOUT,
        ).strip()
        self.info.git = git_version

        try:
            tsvs = {
                Path(path).name: {
                    "Schema": sv.table_schema,
                    "Metadata schema version": sv.version,
                    "Directory schema version": sv.dir_schema,
                }
                for path, sv in self.effective_tsv_paths.items()
            }
            self.info.tsvs = tsvs
        # TODO: inappropriate as preflight error since this gets called after get_errors
        except PreflightError as e:
            self.errors.preflight = str(e)

        return self.info

    def get_errors(self, **kwargs) -> ErrorDict:
        """
        This creates an ErrorDict object
        When converted using ErrorDict.as_dict(), keys are
        present only if there is actually an error to report.
        """
        # plugin_kwargs are passed to the plugin validators via extra_parameters
        kwargs.update(self.extra_parameters)

        # Return if PreflightErrors found
        if self.errors:
            return self.errors

        if not self.effective_tsv_paths:
            self.errors.preflight = "There are no effective TSVs."
            return self.errors

        # Collect errors
        self._get_local_tsv_errors()
        self._get_directory_errors()
        self.validation_routine()
        self._get_reference_errors()

        # Plugin error checking is costly, by default this bails
        # if other errors have been found already and runs plugins if not.
        # Pass in run_plugins=False to skip plugins even if no errors found.
        if self.errors:
            self.errors.plugin_skip = (
                "Skipping plugins validation: errors in upload metadata or dir structure."
            )
        elif self.run_plugins:
            logging.info("Running plugin validation...")
            self.errors.plugin = self._get_plugin_errors(**kwargs)

        return self.errors

    def get_app_context(self, submitted_app_context: Dict):
        """
        Ensure that all default values are present, but privilege any
        submitted values (after making a basic validity check).
        """
        for url_type in ["entities_url", "ingest_url", "constraints_url"]:
            if submitted_app_context.get(url_type):
                split_url = urlsplit(submitted_app_context[url_type])
                assert (
                    split_url.scheme and split_url.netloc
                ), f"{url_type} URL is incomplete: {submitted_app_context[url_type]}"
        self.app_context = {
            "entities_url": "https://entity.api.hubmapconsortium.org/entities/",
            "ingest_url": "https://ingest.api.hubmapconsortium.org/",
            "request_header": {"X-Hubmap-Application": "ingest-pipeline"},
            # TODO: does not work in HuBMAP currently
            "constraints_url": None,
        } | submitted_app_context

    def validation_routine(
        self,
        tsv_paths: Dict[str, SchemaVersion] = {},
    ):
        tsvs_to_evaluate = tsv_paths if tsv_paths else self.effective_tsv_paths
        for tsv_path, schema_version in tsvs_to_evaluate.items():
            self._validate(tsv_path, schema_version)

    def online_checks(
        self,
        tsv_path: str,
        schema: SchemaVersion,
    ):
        url_errors = self._get_url_errors(tsv_path, schema)
        if url_errors:
            self.errors.metadata_url_errors[tsv_path].extend(url_errors)
        try:
            api_errors = self._api_validation(schema)
        except Exception as e:
            api_errors = [e]
        if api_errors:
            self.errors.metadata_validation_api[tsv_path].extend(api_errors)
        constraint_errors = self._constraint_checks(schema)
        if constraint_errors:
            self.errors.metadata_constraint_errors[tsv_path].extend(constraint_errors)

    ###################################
    #
    # Top-level private methods:
    #
    ###################################

    def _get_effective_tsvs(self, tsv_paths: List[str]):
        # TODO: in most/all(?) cases, an upload should only have one assay_type/dir_schema
        # (pending decisions about epics); in that case, the upload itself could probably have props
        # like assay_type, dir_schema, and main_assay_tsv.
        unsorted_effective_tsv_paths = {
            str(path): get_schema_version(
                Path(path),
                self.encoding,
                self.app_context["entities_url"],
                self.app_context["ingest_url"],
                self.globus_token,
                self.directory_path,
            )
            for path in (tsv_paths if tsv_paths else self.directory_path.glob(f"*{TSV_SUFFIX}"))
        }

        self.effective_tsv_paths = {
            k: unsorted_effective_tsv_paths[k] for k in sorted(unsorted_effective_tsv_paths.keys())
        }

    def _check_single_assay(self):
        types_counter = Counter([v.dataset_type for v in self.effective_tsv_paths.values()])
        if len(types_counter.keys()) > 1:
            raise PreflightError(
                f"Found multiple dataset types in upload: {', '.join(types_counter.keys())}"
            )
        repeated = [dataset_type for dataset_type, count in types_counter.items() if count > 1]
        if repeated:
            raise PreflightError(
                f"There is more than one TSV for this type: {', '.join(repeated)}"
            )

    def _get_local_tsv_errors(self):
        for path, schema in self.effective_tsv_paths.items():
            if "data_path" not in schema.rows[0] or "contributors_path" not in schema.rows[0]:
                self.errors.upload_metadata[f"{path} (as {schema.table_schema})"].append(
                    "File is missing data_path or contributors_path."
                )
            for ref in [OtherTypes.CONTRIBUTORS, OtherTypes.ANTIBODIES]:
                errors = self._get_ref_errors(ref, schema, path)
                if errors:
                    self.errors.upload_metadata.update(errors)

    def _get_directory_errors(self):
        if self.is_multi_assay and self.multi_parent:
            for data_path in self.multi_assay_data_paths:
                dir_errors = self._check_data_path(
                    self.multi_parent, Path(self.multi_parent.path), data_path
                )
                for schema in self.effective_tsv_paths.values():
                    if not schema.dataset_type == self.multi_parent.dataset_type:
                        schema.dir_schema = self.multi_parent.dir_schema
                if dir_errors:
                    self.errors.directory.update(dir_errors)
        else:
            for path, schema in self.effective_tsv_paths.items():
                dir_errors = self._get_ref_errors("data", schema, path)
                if dir_errors:
                    self.errors.directory.update(dir_errors)

    def _validate(
        self,
        tsv_path: str,
        schema_version: SchemaVersion,
    ):
        if not schema_version.is_cedar:
            logging.info(
                f"""TSV {tsv_path} does not contain a metadata_schema_id,
                sending for local validation"""
            )
            self._local_validation(tsv_path, schema_version)
        else:
            self.online_checks(tsv_path, schema_version)

    def _local_validation(self, tsv_path: str, schema_version: SchemaVersion):
        try:
            schema = get_table_schema(
                schema_version,
                self.optional_fields,
                self.no_url_checks,
            )
        except Exception as e:
            self.errors.metadata_validation_local.update(
                {f"{tsv_path} (as {schema_version.table_schema})": [str(e)]}
            )
            return
        if schema.get("deprecated") and not self.ignore_deprecation:
            self.errors.metadata_validation_local.update(
                {
                    f"{tsv_path} (as {schema_version.table_schema})": [
                        "Schema version is deprecated"
                    ]
                }
            )
            return

        local_errors = get_table_errors(tsv_path, schema)
        if local_errors:
            self.errors.metadata_validation_local.update(
                {f"{tsv_path} (as {schema_version.table_schema})": local_errors}
            )

    def _api_validation(
        self,
        schema: SchemaVersion,
    ) -> List[Union[str, Dict]]:
        errors = []
        response = cedar_api_call(schema.path)
        if response.status_code != 200:
            raise Exception(response.json())
        elif response.json().get("reporting") and len(response.json().get("reporting")) > 0:
            for error in response.json()["reporting"]:
                errors.append(self._get_message(error))
        else:
            logging.info(f"No errors found during CEDAR validation for {schema.path}!")
            logging.info(f"Response: {response.json()}.")
        return errors

    def _get_url_errors(self, tsv_path: str, schema: SchemaVersion) -> List:
        """
        Check provided values for parent_sample_id and orcid_id; additionally
        check sample_id, organ_id, and source_id values in single TSV validation
        via validation_utils.get_tsv_errors.
        """
        errors = []

        if self.no_url_checks:
            return errors

        constrained_fields = self._get_constrained_fields(schema)

        rows = read_rows(Path(tsv_path), self.encoding)
        fields = rows[0].keys()
        if missing_fields := [k for k in constrained_fields.keys() if k not in fields].sort():
            raise ErrorDictException(f"Missing fields: {missing_fields}")
        url_errors = self._find_and_check_url_fields(rows, constrained_fields, schema)
        return url_errors

    def _constraint_checks(self, schema: SchemaVersion):
        # HuBMAP does not have constraints endpoint, SenNet can pass it in explicitly
        if not self.app_context["constraints_url"]:
            return
        payload = self._construct_constraint_check(schema)
        if not payload:
            print(f"No constraint checks made for schema {schema.schema_name}.")
            return
        data = json.dumps(payload)
        headers = {
            "Authorization": f"Bearer {self.globus_token}",
            "Content-Type": "application/json",
        }
        params = {"match": True, "order": CONSTRAINTS_CHECK_METHOD}
        response = requests.post(
            self.app_context["constraints_url"], headers=headers, data=data, params=params
        )
        if self.verbose:
            print("Ancestor-Descendant pairs sent:")
            self._print_constraint_pairs(payload)
        try:
            response.raise_for_status()
        except Exception:
            return self._get_constraint_check_errors(response, schema)

    def _find_and_check_url_fields(
        self, rows: List, constrained_fields: Dict, schema: SchemaVersion
    ) -> List[Dict[str, str]]:
        errors = []
        for i, row in enumerate(rows):
            url_fields = self._get_url_fields(row, constrained_fields)
            for field_name, field_value in url_fields.items():
                for value in field_value:
                    try:
                        entity_type = self._check_url(
                            field_name, i, value, constrained_fields, schema
                        )
                        if entity_type:
                            schema.ancestor_entities.append(entity_type)
                    except Exception as e:
                        error = {
                            "errorType": type(e).__name__,
                            "column": field_name,
                            "row": i,
                            "value": value,
                            "error_text": e.__str__(),
                        }
                        errors.append(self._get_message(error))
        return errors

    def _get_reference_errors(self):
        no_ref_errors = self.__get_no_ref_errors()
        multi_ref_errors = self.__get_multi_ref_errors()
        shared_dir_errors = self.__get_shared_dir_errors()
        if no_ref_errors:
            self.errors.reference.update({"No References": no_ref_errors})
        if multi_ref_errors:
            self.errors.reference.update({"Multiple References": multi_ref_errors})
        if shared_dir_errors:
            self.errors.reference.update({"Shared Directory References": shared_dir_errors})

    def _get_plugin_errors(self, **kwargs) -> dict:
        plugin_path = self.plugin_directory
        if not plugin_path:
            return {}
        errors: DefaultDict[str, list] = defaultdict(list)
        for metadata_path, sv in self.effective_tsv_paths.items():
            try:
                # If this is not a multi-assay upload, check all files;
                # if this is a multi-assay upload, check all files ONCE
                # using the parent metadata file as a manifest, skipping
                # non-parent dataset_types
                if not self.multi_parent or (sv.dataset_type == self.multi_parent.dataset_type):
                    for k, v in run_plugin_validators_iter(
                        metadata_path,
                        sv,
                        plugin_path,
                        self.is_shared_upload,
                        verbose=self.verbose,
                        **kwargs,
                    ):
                        if v is None:
                            self.info.successful_plugins.append(k.__name__)
                        else:
                            errors[k.description].append(v)
            except PluginValidatorError as e:
                # We are ok with just returning a single error, rather than all.
                errors["Unexpected Plugin Error"] = [e]
        for k, v in errors.items():
            errors[k] = sorted(v)
        return dict(errors)  # get rid of defaultdict

    #################################
    #
    # Multi-assay methods/properties:
    #
    #################################

    @cached_property
    def multi_parent(self) -> Optional[SchemaVersion]:
        multi_assay_parents = [sv for sv in self.effective_tsv_paths.values() if sv.contains]
        if len(multi_assay_parents) == 0:
            return
        if len(multi_assay_parents) > 1:
            raise PreflightError(
                f"Upload contains multiple parent multi-assay types: {', '.join([parent.schema_name for parent in multi_assay_parents])}"
            )
        return multi_assay_parents[0]

    @cached_property
    def multi_components(self) -> List:
        if self.multi_parent:
            return [sv for sv in self.effective_tsv_paths.values() if not sv.contains]
        else:
            return []

    @cached_property
    def multi_assay_data_paths(self) -> List:
        if not self.is_multi_assay or not self.multi_parent:
            return []
        shared_data_paths = [key["data_path"] for key in self.multi_parent.rows]
        return shared_data_paths

    @cached_property
    def is_multi_assay(self) -> bool:
        if self.multi_parent and self.multi_components:
            return True
        return False

    def _check_multi_assay(self):
        # This is not recursive, so if there are nested multi-assay types it will not work
        if self.multi_parent and self.multi_components:
            try:
                self._check_multi_assay_children()
                self._check_data_paths_shared_with_parent()
                logging.info(f"Multi-assay parent: {self.multi_parent.dataset_type}")
                logging.info(
                    f"Multi-assay components: {', '.join([component.dataset_type for component in self.multi_components])}"  # noqa: E501
                )
            except AssertionError as e:
                raise PreflightError(str(e))
        else:
            logging.info("Not a multi-assay upload.")

    def _check_multi_assay_children(self):
        """
        Iterate through child dataset types, check that they are valid
        components of parent multi-assay type and that no components are missing
        """
        assert (
            self.multi_parent and self.multi_components
        ), f"Error validating multi-assay upload, missing parent and/or component values. Parent: {self.multi_parent.dataset_type if self.multi_parent else None} / Components: {[component.dataset_type for component in self.multi_components if self.multi_components]}"  # noqa: E501
        not_allowed = []
        necessary = copy(self.multi_parent.contains)
        for sv in self.multi_components:
            if sv.dataset_type.lower() not in self.multi_parent.contains:
                not_allowed.append(sv.dataset_type)
            else:
                necessary.remove(sv.dataset_type.lower())
        message = ""
        if necessary:
            message += f"Multi-assay parent type {self.multi_parent.dataset_type} missing required component(s): {', '.join(necessary)}."  # noqa: E501
        if not_allowed:
            message += f" Invalid child assay type(s) for parent type {self.multi_parent.dataset_type}: {', '.join(not_allowed)}"  # noqa: E501
        if message:
            raise PreflightError(message)

    def _check_data_paths_shared_with_parent(self):
        """
        Check parent multi-assay TSV data_path values against data_paths in child TSVs
        """
        assert (
            self.multi_parent and self.multi_components
        ), f"Cannot check shared data paths for multi-assay upload, missing parent and/or component values. Parent: {self.multi_parent.dataset_type if self.multi_parent else None} / Components: {[component.dataset_type for component in self.multi_components if self.multi_components]}"  # noqa: E501
        # Make sure that neither parents nor components have any unique paths, as this
        # indicates either a missing component or a dataset that is unique to a
        # component; collect any/all errors
        errors = []
        for component in self.multi_components:
            component_paths = {row.get("data_path") for row in component.rows}
            unique_in_component = component_paths.difference(self.multi_assay_data_paths)
            if unique_in_component:
                errors.append(
                    f"Path(s) in {component.dataset_type} metadata TSV not present in parent: {', '.join(unique_in_component)}."  # noqa: E501
                )
            unique_in_parent = set(self.multi_assay_data_paths).difference(component_paths)
            if unique_in_parent:
                errors.append(
                    f"Path(s) in {self.multi_parent.dataset_type} metadata TSV not present in component {component.dataset_type}: {', '.join(unique_in_parent)}."  # noqa: E501
                )
        if errors:
            raise PreflightError(" ".join(errors))

    ##############################
    #
    # Supporting private methods:
    #
    ##############################

    def _get_constrained_fields(self, schema: SchemaVersion):
        # assay -> parent_sample_id
        # sample -> sample_id
        # organ -> organ_id
        # contributors -> orcid (new) / orcid_id (old)

        constrained_fields = {}
        schema_name = schema.schema_name
        entities_url = self.app_context.get("entities_url")

        if schema_name in [
            OtherTypes.SOURCE,
            *Sample.with_parent_type(),
        ]:
            constrained_fields["source_id"] = entities_url
            if schema_name in Sample.with_parent_type():
                constrained_fields["sample_id"] = entities_url
        elif schema_name in OtherTypes.ORGAN:  # Deprecated, included for backward-compatibility
            constrained_fields["organ_id"] = entities_url
        elif schema_name == OtherTypes.CONTRIBUTORS:
            if schema.is_cedar:
                constrained_fields["orcid"] = "https://pub.orcid.org/v3.0/expanded-search/"
            else:
                constrained_fields["orcid_id"] = "https://pub.orcid.org/v3.0/expanded-search/"
        else:
            constrained_fields["parent_sample_id"] = entities_url
        return constrained_fields

    def _get_url_fields(
        self,
        row: Dict,
        constrained_fields: dict,
    ) -> Dict[str, List[str]]:
        url_fields = {}
        check = {k: v for k, v in row.items() if k in constrained_fields}
        for check_field, value in check.items():
            if check_field in self.check_fields and not self.globus_token:
                raise ErrorDictException(
                    "No token received to check URL fields against Entity API."
                )
            # TODO: could just split if there's a comma in the field
            elif check_field == "parent_sample_id":
                url_fields["parent_sample_id"] = value.split(",")
            else:
                url_fields[check_field] = [value]
        return url_fields

    def _check_url(
        self, field: str, row: int, value: str, constrained_fields: Dict, schema: SchemaVersion
    ) -> Optional[AncestorTypeInfo]:
        """
        Returns entity_type if checking a field in check_fields.
        """
        url = urljoin(constrained_fields[field], value)
        if field in self.check_fields:
            headers = self.app_context.get("request_header", {})
            response = get_entity_api_data(url, self.globus_token, headers)
            if (
                not (schema.schema_name == OtherTypes.SAMPLE and field == "sample_id")
                and not schema.schema_name == OtherTypes.SOURCE
            ):
                return AncestorTypeInfo(
                    entity_id=value,
                    source_schema=schema,
                    row=row,
                    column=field,
                    *get_entity_type_vals(response.json()),
                )
        elif field in ["orcid_id", "orcid"]:
            headers = {"Accept": "application/json"}
            response = requests.get(
                constrained_fields[field], headers=headers, params={"q": f"orcid:{value}"}
            )
            num_found = response.json().get("num-found")
            if num_found == 1:
                return
            elif num_found == 0:
                raise Exception(f"ORCID {value} does not exist.")
            else:
                raise Exception(f"Found {num_found} matches for ORCID {value}.")
        else:
            response = requests.get(url)
            response.raise_for_status()

    def _construct_constraint_check(self, schema: SchemaVersion) -> list[dict]:
        payload = []
        assert isinstance(schema.entity_type_info, EntityTypeInfo), Exception(
            f"Entity type info not present in {schema.schema_name} schema."
        )
        descendant_data = schema.entity_type_info.format_constraint_check_data()
        for ancestor_entity in schema.ancestor_entities:
            payload.append(
                {
                    "ancestors": ancestor_entity.format_constraint_check_data(),
                    "descendants": descendant_data,
                }
            )
        return payload

    def _print_constraint_pairs(self, constraint_list):
        for row in constraint_list:
            row_output = []
            for v in row.values():
                entity_type = v.get("entity_type")
                sub_type = v.get("sub_type")
                if type(sub_type) is list:
                    sub_type = ", ".join(sub_type)
                sub_type_val = v.get("sub_type_val")
                if type(sub_type_val) is list:
                    sub_type_val = ", ".join(sub_type_val)
                row_output.append(
                    f"{entity_type}{f'/{sub_type}' if sub_type else ''}{f'/{sub_type_val}' if sub_type_val else ''}"
                )
            print(" - ".join(row_output))

    def _get_constraint_check_errors(
        self,
        response: requests.Response,
        schema: SchemaVersion,
    ) -> List[str]:
        problem_entities = []
        assert schema.entity_type_info
        if response.status_code == 400:
            for i, entity_check in enumerate(response.json().get("description", [])):
                if entity_check["code"] != 200:
                    ancestors = schema.ancestor_entities[i].format_constraint_check_error()
                    error = {
                        "errorType": "Invalid Ancestor",
                        "column": schema.ancestor_entities[i].column,
                        "row": schema.ancestor_entities[i].row,
                        "value": schema.ancestor_entities[i].entity_id,
                        "error_text": f"Invalid ancestor type for TSV type {schema.entity_type_info.format_constraint_check_error()}. Data sent for ancestor {schema.ancestor_entities[i].entity_id}: {ancestors}.",
                    }
                    problem_entities.append(self._get_message(error))
        return problem_entities

    def _get_message(
        self,
        error: Dict[str, str],
    ) -> Union[str, Dict]:
        """
        >>> u = Upload(Path("/test/dir"))
        >>> print(
        ...     u._get_message(
        ...         {
        ...             'errorType': 'notStandardTerm',
        ...             'column': 'stain_name',
        ...             'row': 1,
        ...             'repairSuggestion': 'H&E',
        ...             'value': 'H& E'
        ...         }
        ...     )
        ... )
        On row 1, column "stain_name", value "H& E" fails because of error "notStandardTerm". Example: H&E
        """  # noqa: E501

        example = error.get("repairSuggestion", "")
        error_text = error.get("error_text", "")

        return_str = self.report_type is ReportType.STR
        if "errorType" in error and "column" in error and "row" in error and "value" in error:
            assert type(error["row"]) is int
            error["row"] = error["row"] + 2
            # This may need readability improvements
            msg = (
                f'On row {error["row"]}, column "{error["column"]}", '
                f'value "{error["value"]}" fails because of error "{error["errorType"]}"'
                f'{f": {error_text}" if error_text else error_text}'
                f'{f". Example: {example}" if example else example}'
            )
            return msg if return_str else get_json(msg, error["row"], error["column"])
        return error

    def _check_path(
        self,
        path_value: str,
        ref: str,
        schema_version: SchemaVersion,
        metadata_path: Union[str, Path],
    ) -> Optional[Dict[str, List[str]]]:
        if ref == "data":
            errors = self._check_data_path(schema_version, Path(metadata_path), path_value)
            if errors:
                self.errors.directory.update(errors)
        else:
            other_path = self.directory_path / path_value
            try:
                assert other_path.exists()
            except AssertionError:
                self.errors.upload_metadata[str(metadata_path)].append(
                    f"Value '{path_value}' in column '{ref}_path' points to non-existent file: '{self.directory_path / path_value}'"
                )
                return
            try:
                self._check_other_path(str(other_path))
            except PreflightError as e:
                self.errors.upload_metadata[str(metadata_path)].append(
                    f"Error opening or reading value '{path_value}' from column '{ref}_path': {e.errors}"
                )

    def _get_ref_errors(
        self,
        ref: str,
        schema: SchemaVersion,
        metadata_path: Union[str, Path],
    ):
        # We don't want to continuously validate shared paths, e.g. contributors.tsv,
        # so this ensures we only check unique paths in a single metadata TSV once
        unique_paths = set()
        for row in schema.rows:
            field = f"{ref}_path"
            if not row.get(field):
                continue
            unique_paths.add(row[field])
        if ref == OtherTypes.CONTRIBUTORS:
            schema.contributors_paths = [
                str(Path(Path(metadata_path).parent, path)) for path in unique_paths
            ]
        elif ref == OtherTypes.ANTIBODIES:
            schema.antibodies_paths = [
                str(Path(Path(metadata_path).parent, path)) for path in unique_paths
            ]
        for path_value in sorted(unique_paths):
            self._check_path(path_value, ref, schema, metadata_path)

    def _check_data_path(
        self, schema_version: SchemaVersion, metadata_path: Path, path_value: str
    ) -> Dict[str, List[str]]:
        errors = {}
        data_path = Path(path_value)
        print_path = str(Path(self.directory_path / data_path))

        if not schema_version.dir_schema:
            raise Exception(
                f"No directory schema found for data_path " f"{print_path} in {metadata_path}!"
            )

        try:
            ref_errors = get_data_dir_errors(
                schema_version.dir_schema,
                root_path=self.directory_path,
                data_dir_path=data_path,
                dataset_ignore_globs=self.dataset_ignore_globs,
            ).popitem()
            if type(ref_errors[1]) is list:
                errors[f"{print_path} (as {ref_errors[0]})"] = ref_errors[1]
            schema_version.dir_schema = ref_errors[0]
        except FileNotFoundError:
            self.errors.directory[str(metadata_path)].append(
                f"Value '{path_value}' in column 'data_path' points to non-existent directory: '{self.directory_path / path_value}'"
            )
        except Exception as e:
            errors[print_path] = e
        return errors

    def _check_other_path(self, other_path: str):
        schema = get_schema_version(
            Path(other_path),
            self.encoding,
            self.app_context["entities_url"],
            self.app_context["ingest_url"],
            self.globus_token,
            self.directory_path,
        )
        self.validation_routine(tsv_paths={str(other_path): schema})

    def __get_no_ref_errors(self) -> dict:
        referenced_data_paths = (
            set(self.__get_data_references().keys())
            | set(self.__get_contributors_references().keys())
            | set(self.__get_antibodies_references().keys())
        )

        referenced_data_paths = {Path(path) for path in referenced_data_paths}

        non_metadata_paths = {
            Path(path.name)
            for path in self.directory_path.iterdir()
            if not path.name.endswith(TSV_SUFFIX)
            and not any([fnmatch(path.name, glob) for glob in self.upload_ignore_globs])
        }
        unreferenced_paths = non_metadata_paths - referenced_data_paths
        unreferenced_dir_paths = [path for path in unreferenced_paths if Path(path).is_dir()]
        unreferenced_file_paths = [path for path in unreferenced_paths if not Path(path).is_dir()]
        errors = {}
        if unreferenced_dir_paths:
            errors["Directories"] = unreferenced_dir_paths
        if unreferenced_file_paths:
            errors["Files"] = unreferenced_file_paths
        return errors

    def __get_shared_dir_errors(self) -> dict:
        errors = {}
        all_non_global_files = self.__get_non_global_files_references()
        if all_non_global_files:
            for row_non_global_files, row_references in all_non_global_files.items():
                row_non_global_files = {
                    (self.directory_path / "./non_global" / Path(x.strip())): Path(x.strip())
                    for x in row_non_global_files.split(";")
                    if x.strip()
                }

                for (
                    full_path_row_non_global_file,
                    rel_path_row_non_global_file,
                ) in row_non_global_files.items():
                    if not full_path_row_non_global_file.exists():
                        errors[",".join(row_references)] = (
                            f"{rel_path_row_non_global_file} not exist in upload."
                        )
        else:
            # Catch case 2
            if self.is_shared_upload:
                errors["Upload Errors"] = (
                    "No non_global_files specified but "
                    "upload has global & non_global directories"
                )

        return errors

    def __get_multi_ref_errors(self) -> dict:
        #  If - multi-assay dataset (and only that dataset is referenced) don't fail
        #  Else - fail
        errors = {}
        data_references = self.__get_data_references()
        for path, references in data_references.items():
            if path not in self.multi_assay_data_paths:
                if len(references) > 1 and not self.is_shared_upload:
                    errors[path] = references
        return errors

    def __get_data_references(self) -> dict:
        return self.__get_references("data_path")

    def __get_antibodies_references(self) -> dict:
        return self.__get_references("antibodies_path")

    def __get_contributors_references(self) -> dict:
        return self.__get_references("contributors_path")

    def __get_non_global_files_references(self) -> dict:
        return self.__get_references("non_global_files")

    def __get_references(self, col_name) -> dict:
        references = defaultdict(list)
        for tsv_path, schema in self.effective_tsv_paths.items():
            for i, row in enumerate(schema.rows):
                if col_name in row:
                    reference = f"{tsv_path} (row {i+2})"
                    references[row[col_name]].append(reference)
        return dict(references)
