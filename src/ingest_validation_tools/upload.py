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
from typing import Optional, Union
from urllib.parse import urljoin, urlsplit

import requests

from ingest_validation_tools.enums import OtherTypes, Sample
from ingest_validation_tools.error_report import (
    Error,
    ErrorTypes,
    ValidationReport,
    ValidationSerializer,
)
from ingest_validation_tools.plugin_validator import (
    ValidatorError as PluginValidatorError,
)
from ingest_validation_tools.plugin_validator import (
    run_plugin_validators_iter,
)
from ingest_validation_tools.schema_loader import (
    AncestorTypeInfo,
    EntityTypeInfo,
    PreflightError,
    SchemaVersion,
    get_table_schema,
)
from ingest_validation_tools.table_validator import ReportType, get_table_errors
from ingest_validation_tools.validation_utils import (
    cedar_validation_call,
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
        run_plugins: Optional[bool] = None,
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
            "parent_dataset_id",
            "source_id",
            "sample_id",
        ]

        self.report = ValidationReport()
        self.get_app_context(app_context)

        try:
            self._get_effective_tsvs(tsv_paths)
            self._check_multi_assay()
            if not self.is_multi_assay:
                self._check_single_assay()

            self.is_shared_upload = {"global", "non_global"} == {
                x.name
                for x in self.directory_path.glob("*global")
                if x.is_dir() and x.name in ["global", "non_global"]
            }

        except PreflightError as e:
            self.errors(ErrorTypes.PREFLIGHT, str(e))

        self._populate_validation_report_info()

    #####################
    #
    # Public methods:
    #
    #####################

    def get_errors(self, **kwargs):
        """
        Legacy API.
        """
        self.validate(**kwargs)

    # @overload
    # def validate(self, as_yaml: Literal[True], **kwargs: Any) -> str:
    #     ...  # mypy: ignore
    #
    # @overload
    # def validate(self, as_yaml: Literal[False] = False, **kwargs: Any) -> dict:
    #     ...  # mypy: ignore
    #
    def validate(self, as_yaml: bool = False, **kwargs):
        """
        Run validation and return serialized errors.
        Can pass kwargs to plugins and serializer.
        By default returns JSON but can return YAML string with as_yaml=True.
        On success returns empty dict/str (or detailed info on run if
                               detailed_validation_report=True)
        """
        if self.report.errors:
            # Preflight errors found, return early
            plugins_ran = False
        else:
            # Collect errors
            self._get_local_tsv_errors()
            self._get_directory_errors()
            self.validation_routine()
            self._get_reference_errors()
            self._run_plugins(**kwargs)
            plugins_ran = bool(self.run_plugins)

        self.report.validation_completed = True
        return ValidationSerializer(
            self.report, plugins_ran=plugins_ran, as_yaml=as_yaml, **kwargs
        ).serialize()

    ###########
    # Helpers #
    ###########

    def errors(self, error_type: ErrorTypes, error_content: Union[dict, list, str], **kwargs):
        """
        Helper method for adding to error report.
        Minimal call to add error: self.errors(ErrorTypes.TYPE, content)
        Maximal call can also include the following kwargs:
            errorType: str
            file: str | Path
            schema: str
            column: str
            row: int
            value: str
        """
        error = Error(error_type, error_content, **kwargs)
        self.report.errors.append(error)

    def get_app_context(self, submitted_app_context: dict):
        """
        Ensure that all default values are present, but privilege any
        submitted values (after making a basic validity check).
        """
        for url_type in ["entities_url", "ingest_url", "constraints_url", "uuid_url"]:
            if submitted_app_context.get(url_type):
                split_url = urlsplit(submitted_app_context[url_type])
                assert (
                    split_url.scheme and split_url.netloc
                ), f"{url_type} URL is incomplete: {submitted_app_context[url_type]}"
        # TODO: abstract
        self.app_context = {
            "entities_url": "https://entity.api.hubmapconsortium.org/entities/",
            "ingest_url": "https://ingest.api.hubmapconsortium.org/",
            "request_header": {"X-Hubmap-Application": "ingest-pipeline"},
            # TODO: add
            "constraints_url": None,
            "uuid_url": "https://uuid.api.hubmapconsortium.org/uuid/",
        } | submitted_app_context

    def validation_routine(
        self,
        tsv_paths: dict[str, SchemaVersion] = {},
    ):
        tsvs_to_evaluate = tsv_paths if tsv_paths else self.effective_tsv_paths
        for tsv_path, schema_version in tsvs_to_evaluate.items():
            self._validate(tsv_path, schema_version)

    def online_checks(
        self,
        tsv_path: str,
        schema: SchemaVersion,
    ):
        self._get_url_errors(tsv_path, schema)
        self._api_validation(schema)
        self._constraint_checks(schema)

    ###################################
    #
    # Top-level private methods:
    #
    ###################################

    def _populate_validation_report_info(self):
        self.report.time = datetime.now()
        self.report.base_path = str(self.directory_path)
        self.report.git = subprocess.check_output(
            "git rev-parse --short HEAD".split(" "),
            encoding="ascii",
            stderr=subprocess.STDOUT,
        ).strip()
        tsvs = {
            Path(path).name: {
                "Metadata type": sv.dataset_type if sv.is_cedar else sv.table_schema,
                "Metadata version": sv.version,
                "Directory schema version": sv.dir_schema,
            }
            for path, sv in self.effective_tsv_paths.items()
        }
        self.report.tsvs = tsvs

    def _get_effective_tsvs(self, tsv_paths: list[str]):
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
        if not self.effective_tsv_paths:
            self.errors(ErrorTypes.PREFLIGHT, "There are no metadata TSVs.")

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
                self.errors(
                    ErrorTypes.UPLOAD_METADATA,
                    "File is missing data_path or contributors_path.",
                    file=path,
                    schema=schema.table_schema,
                )
            for ref in [OtherTypes.CONTRIBUTORS, OtherTypes.ANTIBODIES]:
                self._get_ref_errors(ref, schema, path)

    def _get_directory_errors(self):
        if self.is_multi_assay and self.multi_parent:
            for data_path in self.multi_assay_data_paths:
                self._check_data_path(self.multi_parent, Path(self.multi_parent.path), data_path)
                for schema in self.effective_tsv_paths.values():
                    if not schema.dataset_type == self.multi_parent.dataset_type:
                        schema.dir_schema = self.multi_parent.dir_schema
        else:
            for path, schema in self.effective_tsv_paths.items():
                self._get_ref_errors("data", schema, path)

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
            self.errors(
                ErrorTypes.METADATA_VALIDATION_LOCAL,
                str(e),
                file=tsv_path,
                schema=schema_version.table_schema,
            )
            return
        if schema.get("deprecated") and not self.ignore_deprecation:
            self.errors(
                ErrorTypes.METADATA_VALIDATION_LOCAL,
                "Schema version is deprecated",
                file=tsv_path,
                schema=schema_version.table_schema,
            )
            return

        local_errors = get_table_errors(tsv_path, schema)
        if local_errors:
            for error in local_errors:
                self.errors(
                    ErrorTypes.METADATA_VALIDATION_LOCAL,
                    error,
                    file=tsv_path,
                    schema=schema_version.table_schema,
                )

    def _api_validation(
        self,
        schema: SchemaVersion,
    ) -> list[Union[str, dict]]:
        errors = []
        response = cedar_validation_call(schema.path)
        if response.status_code != 200:
            self.errors(ErrorTypes.METADATA_VALIDATION_API, response.json())
        elif response.json().get("reporting") and len(response.json().get("reporting")) > 0:
            for error in response.json()["reporting"]:
                # TODO: file, fix get_msg
                self.errors(
                    ErrorTypes.METADATA_VALIDATION_API,
                    f"{error.get('error_message')} Example: {error.get('repairSuggestion')}",
                    errorType=error.get("errorType"),
                    file=None,
                    column=error.get("column"),
                    row=error.get("row"),
                    value=error.get("value"),
                )

        else:
            logging.info(f"No errors found during CEDAR validation for {schema.path}!")
            logging.info(f"Response: {response.json()}.")
        return errors

    def _get_url_errors(self, tsv_path: str, schema: SchemaVersion):
        """
        Check provided values for parent_sample_id and orcid_id; additionally
        check sample_id, organ_id, and source_id values in single TSV validation
        via validation_utils.get_tsv_errors.
        """
        if self.no_url_checks:
            return

        constrained_fields = self._get_constrained_fields(schema)

        rows = read_rows(Path(tsv_path), self.encoding)
        fields = rows[0].keys()
        if missing_fields := [k for k in constrained_fields.keys() if k not in fields].sort():
            raise Exception(f"Missing fields: {missing_fields}")
        self._find_and_check_url_fields(rows, constrained_fields, schema, Path(tsv_path))

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
            self._get_constraint_check_errors(response, schema)

    def _find_and_check_url_fields(
        self, rows: list, constrained_fields: dict, schema: SchemaVersion, tsv_path: Path
    ):
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
                        self.errors(
                            ErrorTypes.METADATA_VALIDATION_URLS,
                            e.__str__(),
                            errorType=type(e).__name__,
                            file=tsv_path,
                            column=field_name,
                            row=i,
                            value=value,
                        )

    def _get_reference_errors(self):
        no_ref_errors = self.__get_no_ref_errors()
        multi_ref_errors = self.__get_multi_ref_errors()
        shared_dir_errors = self.__get_shared_dir_errors()
        if no_ref_errors:
            self.errors(ErrorTypes.REFERENCE, {"No References": no_ref_errors})
        if multi_ref_errors:
            self.errors(ErrorTypes.REFERENCE, {"Multiple References": multi_ref_errors})
        if shared_dir_errors:
            self.errors(ErrorTypes.REFERENCE, {"Shared Directory References": shared_dir_errors})

    def _get_plugin_errors(self, **kwargs):
        plugin_path = self.plugin_directory
        if not plugin_path:
            return {}
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
                        globus_token=self.globus_token,
                        app_context=self.app_context,
                        **kwargs,
                    ):
                        if v is None:
                            self.report.successful_plugins.append(k.__name__)
                        else:
                            self.errors(ErrorTypes.PLUGIN, v, schema=k.description)
            except PluginValidatorError as e:
                # We are ok with just returning a single error, rather than all.
                self.errors(ErrorTypes.PLUGIN, str(e), errorType="Unexpected Plugin Error")

    def _run_plugins(self, **kwargs):
        # Plugin error checking is costly; by default this bails
        # if other errors have been found already and runs plugins if not.
        # Pass in run_plugins bool to modify behavior.
        if self.run_plugins is None:  # default behavior
            if self.report.errors:  # errors found, skip
                self.errors(
                    ErrorTypes.PLUGIN,
                    "Skipping plugins validation: errors in upload metadata or dir structure.",
                )
            else:  # no errors, run plugins
                logging.info("Running plugin validation...")
                self._get_plugin_errors(**kwargs)
        elif self.run_plugins:
            logging.info("Running plugin validation...")
            self._get_plugin_errors(**kwargs)
        else:
            logging.info("Skipping plugin validation.")

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
    def multi_components(self) -> list:
        if self.multi_parent:
            return [sv for sv in self.effective_tsv_paths.values() if not sv.contains]
        else:
            return []

    @cached_property
    def multi_assay_data_paths(self) -> list:
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
        row: dict,
        constrained_fields: dict,
    ) -> dict[str, list[str]]:
        url_fields = {}
        check = {k: v for k, v in row.items() if k in constrained_fields}
        for check_field, value in check.items():
            if check_field in self.check_fields and not self.globus_token:
                raise Exception("No token received to check URL fields against Entity API.")
            if check_field in ["parent_sample_id", "parent_dataset_id"]:
                url_fields[check_field] = value.split(",")
            else:
                url_fields[check_field] = [value]
        return url_fields

    def _check_url(
        self, field: str, row: int, value: str, constrained_fields: dict, schema: SchemaVersion
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
    ):
        assert schema.entity_type_info
        if response.status_code == 400:
            for i, entity_check in enumerate(response.json().get("description", [])):
                if entity_check["code"] != 200:
                    ancestors = schema.ancestor_entities[i].format_constraint_check_error()
                    # TODO: file, get_msg
                    self.errors(
                        ErrorTypes.METADATA_VALIDATION_CONSTRAINTS,
                        f"Invalid ancestor type for TSV type {schema.entity_type_info.format_constraint_check_error()}. Data sent for ancestor {schema.ancestor_entities[i].entity_id}: {ancestors}.",
                        errorType="Invalid Ancestor",
                        file=None,
                        column=schema.ancestor_entities[i].column,
                        row=schema.ancestor_entities[i].row,
                        value=schema.ancestor_entities[i].entity_id,
                    )

    def _get_message(
        self,
        error: dict[str, str],
    ) -> Union[str, dict]:
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
                f'value "{error["value"]}" fails because of error "{error["errorType"]}"'
                f'{f": {error_text}" if error_text else error_text}'
                f'{f". Example: {example}" if example else example}'
            )
            full_msg = f'On row {error["row"]}, column "{error["column"]}", {msg}'
            return full_msg if return_str else get_json(msg, error["row"], error["column"])
        return error

    def _check_path(
        self,
        path_value: str,
        ref: str,
        schema_version: SchemaVersion,
        metadata_path: Union[str, Path],
    ) -> Optional[dict[str, list[str]]]:
        if ref == "data":
            self._check_data_path(schema_version, Path(metadata_path), path_value)
        else:
            other_path = self.directory_path / path_value
            try:
                assert other_path.exists()
            except AssertionError:
                self.errors(
                    ErrorTypes.UPLOAD_METADATA,
                    f"Value '{path_value}' in column '{ref}_path' points to non-existent file: '{self.directory_path / path_value}'",
                    file=metadata_path,
                    value=path_value,
                )
                return
            try:
                self._check_other_path(str(other_path))
            except PreflightError as e:
                self.errors(
                    ErrorTypes.UPLOAD_METADATA,
                    f"Error opening or reading value '{path_value}' from column '{ref}_path': {e.errors}",
                    file=metadata_path,
                    column=f"{ref}_path",
                    value=path_value,
                )

    def _get_ref_errors(
        self,
        ref: Union[str, OtherTypes],
        schema: SchemaVersion,
        metadata_path: Union[str, Path],
    ):
        # We don't want to continuously validate shared paths, e.g. contributors.tsv,
        # so this ensures we only check unique paths in a single metadata TSV once
        unique_paths = set()
        if isinstance(ref, OtherTypes):
            ref = ref.value
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
    ):
        data_path = Path(path_value)
        print_path = str(Path(self.directory_path / data_path))

        if not schema_version.dir_schema:
            self.errors(
                ErrorTypes.DIRECTORY,
                f"No directory schema found for data_path {print_path}.",
                value=path_value,
            )
            return

        try:
            ref_errors = get_data_dir_errors(
                schema_version.dir_schema,
                root_path=self.directory_path,
                data_dir_path=data_path,
                dataset_ignore_globs=self.dataset_ignore_globs,
            ).popitem()
            if type(ref_errors[1]) is list:
                for error in ref_errors[1]:
                    self.errors(
                        ErrorTypes.DIRECTORY,
                        error,
                        schema=ref_errors[0],
                    )
            schema_version.dir_schema = ref_errors[0]
        except FileNotFoundError:
            self.errors(
                ErrorTypes.UPLOAD_METADATA,
                f"Value '{path_value}' in column 'data_path' points to non-existent directory: '{self.directory_path / path_value}",
                file=metadata_path,
                value=path_value,
            )
        except Exception as e:
            self.errors(ErrorTypes.DIRECTORY, str(e), file=print_path)

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
        unreferenced_dir_paths = [
            str(path) for path in unreferenced_paths if Path(self.directory_path, path).is_dir()
        ]
        unreferenced_file_paths = [
            str(path)
            for path in unreferenced_paths
            if not Path(self.directory_path, path).is_dir()
        ]
        errors = {}
        if unreferenced_dir_paths:
            errors["Directories"] = unreferenced_dir_paths
        if unreferenced_file_paths:
            errors["Files"] = unreferenced_file_paths
        return errors

    def __get_shared_dir_errors(self) -> dict:
        all_non_global_files = self.__get_non_global_files_references()
        if all_non_global_files:
            errors = defaultdict(list)
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
                        errors[",".join(row_references)].append(
                            f"{full_path_row_non_global_file} does not exist in upload; is {rel_path_row_non_global_file} in the non_global directory?"
                        )
        else:
            # Catch case 2
            errors = {}
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
                    reference = f"{tsv_path} (row {i + 2})"
                    references[row[col_name]].append(reference)
        return dict(references)
