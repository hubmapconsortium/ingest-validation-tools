from __future__ import annotations

import logging
import subprocess
from collections import Counter, defaultdict
from copy import copy
from datetime import datetime
from fnmatch import fnmatch
from functools import cached_property
from pathlib import Path
from typing import Any, DefaultDict, Dict, List, Optional, Union

import requests

from ingest_validation_tools.plugin_validator import (
    ValidatorError as PluginValidatorError,
)
from ingest_validation_tools.plugin_validator import run_plugin_validators_iter
from ingest_validation_tools.schema_loader import (
    PreflightError,
    SchemaVersion,
    get_table_schema,
)
from ingest_validation_tools.table_validator import ReportType, get_table_errors
from ingest_validation_tools.validation_utils import (
    get_data_dir_errors,
    get_json,
    get_schema_version,
    read_rows,
)

TSV_SUFFIX = "metadata.tsv"


class ErrorDictException(Exception):
    def __init__(self, errors):
        message = f"Halting compilation of errors after detecting the following errors: {errors}."
        super().__init__(message)
        labeled_errors = {}
        labeled_errors["Fatal Exception"] = errors
        self.errors = labeled_errors


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
        offline: bool = False,
        ignore_deprecation: bool = False,
        extra_parameters: Union[dict, None] = None,
        globus_token: str = "",
        app_context: dict = {},
        run_plugins: bool = False,
        verbose: bool = True,
    ):
        self.directory_path = directory_path
        self.optional_fields = optional_fields
        self.dataset_ignore_globs = dataset_ignore_globs
        self.upload_ignore_globs = upload_ignore_globs
        self.plugin_directory = plugin_directory
        self.encoding = encoding
        self.offline = offline
        self.add_notes = add_notes
        self.ignore_deprecation = ignore_deprecation
        self.errors = {}
        self.effective_tsv_paths = {}
        self.extra_parameters = extra_parameters if extra_parameters else {}
        self.globus_token = globus_token
        self.run_plugins = run_plugins
        self.verbose = verbose

        self.get_app_context(app_context)

        try:
            unsorted_effective_tsv_paths = {
                str(path): get_schema_version(
                    path,
                    self.encoding,
                    self.app_context["ingest_url"],
                    self.directory_path,
                    offline=self.offline,
                )
                for path in (tsv_paths if tsv_paths else directory_path.glob(f"*{TSV_SUFFIX}"))
            }

            self.effective_tsv_paths = {
                k: unsorted_effective_tsv_paths[k]
                for k in sorted(unsorted_effective_tsv_paths.keys())
            }

            self._check_multi_assay()
            if not self.is_multi_assay:
                self._check_single_assay()

            self.is_shared_upload = {"global", "non_global"} == {
                x
                for x in self.directory_path.glob("*global")
                if x.is_dir() and x.name in ["global", "non_global"]
            }

        except PreflightError as e:
            self.errors["Preflight"] = e

    #####################
    #
    # Public methods:
    #
    #####################

    # TODO: this would be better in a config so it could be shared with
    # validation_utils.get_assaytype_data / would not conflict with SenNet values
    # For the moment, ingest_url is just hard-coded in get_assaytype_data
    # to allow validate_tsv.py to run
    def get_app_context(self, submitted_app_context: Dict):
        default_app_context = {
            "entities_url": "https://entity.api.hubmapconsortium.org/entities/",
            "ingest_url": "https://ingest.api.hubmapconsortium.org/",
            "request_header": {"X-Hubmap-Application": "ingest-pipeline"},
        }
        if {*default_app_context} - {*submitted_app_context}:
            diff = {*default_app_context} - {*submitted_app_context}
            submitted_app_context.update({key: default_app_context[key] for key in diff})
        self.app_context = submitted_app_context

    def get_info(self) -> dict:
        git_version = subprocess.check_output(
            "git rev-parse --short HEAD".split(" "),
            encoding="ascii",
            stderr=subprocess.STDOUT,
        ).strip()

        # If called before get_errors, will report dir schema major version only

        try:
            effective_tsvs = {
                Path(path).name: {
                    "Schema": sv.table_schema,
                    "Metadata schema version": sv.version,
                    "Directory schema version": sv.dir_schema,
                }
                for path, sv in self.effective_tsv_paths.items()
            }
            return {
                "Time": datetime.now(),
                "Git version": git_version,
                "Directory": str(self.directory_path),
                "TSVs": effective_tsvs,
            }
        except PreflightError as e:
            self.errors["Preflight"] = e
            return self.errors

    def get_errors(self, **kwargs) -> dict:
        # This creates a deeply nested dict.
        # Keys are present only if there is actually an error to report.
        # plugin_kwargs are passed to the plugin validators.

        kwargs.update(self.extra_parameters)
        if self.errors:
            return self.errors

        if not self.effective_tsv_paths:
            return {"Missing": "There are no effective TSVs."}

        errors = {}
        try:
            upload_errors = self._check_upload()
            if upload_errors:
                errors["Upload Errors"] = upload_errors

            validation_errors = self.validation_routine()
            if validation_errors:
                errors["Metadata TSV Validation Errors"] = validation_errors

            reference_errors = self._get_reference_errors()
            if reference_errors:
                errors["Reference Errors"] = reference_errors

            if errors and not self.run_plugins:
                raise ErrorDictException(
                    "Skipping plugins validation: errors in upload metadata or dir structure."
                )

            elif self.run_plugins:
                logging.info("Running plugin validation...")

            plugin_errors = self._get_plugin_errors(**kwargs)
            if plugin_errors:
                errors["Plugin Errors"] = plugin_errors
        except ErrorDictException as e:
            return errors | e.errors

        return errors

    def validation_routine(
        self,
        report_type: ReportType = ReportType.STR,
        tsv_paths: Dict[str, SchemaVersion] = {},
    ) -> dict:
        errors: DefaultDict[str, dict] = defaultdict(dict)
        tsvs_to_evaluate = tsv_paths if tsv_paths else self.effective_tsv_paths
        for tsv_path, schema_version in tsvs_to_evaluate.items():
            path_errors = self._validate(tsv_path, schema_version, report_type)
            if not path_errors:
                continue
            for key, value in path_errors.items():
                if type(value) is dict:
                    errors[key].update(value)
                else:
                    errors.update({key: value})
        return dict(errors)

    ###################################
    #
    # Top-level private methods:
    #
    ###################################

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

    def _check_upload(self) -> dict:
        upload_errors = {}
        tsv_errors = self._get_local_tsv_errors()
        if tsv_errors:
            upload_errors["TSV Errors"] = tsv_errors
        dir_errors = self._get_directory_errors()
        if dir_errors:
            upload_errors["Directory Errors"] = dir_errors
        return upload_errors

    def _get_local_tsv_errors(self) -> Optional[Dict]:
        errors: DefaultDict[str, list] = defaultdict(list)
        for path, schema in self.effective_tsv_paths.items():
            if "data_path" not in schema.rows[0] or "contributors_path" not in schema.rows[0]:
                errors.update(
                    {
                        f"{path} (as {schema.table_schema})": [
                            "File is missing data_path or contributors_path."
                        ]
                    }
                )
            for ref in ["contributors", "antibodies"]:
                ref_errors = self._get_ref_errors(ref, schema, path)
                if ref_errors:
                    errors.update(ref_errors)
        return errors

    def _get_directory_errors(self) -> dict:
        errors = {}
        if self.is_multi_assay and self.multi_parent:
            for data_path in self.multi_assay_data_paths:
                dir_errors = self._check_data_path(
                    self.multi_parent, Path(self.multi_parent.path), data_path
                )
                for schema in self.effective_tsv_paths.values():
                    if not schema.dataset_type == self.multi_parent.dataset_type:
                        schema.dir_schema = self.multi_parent.dir_schema
                if dir_errors:
                    errors.update(dir_errors)
        else:
            for path, schema in self.effective_tsv_paths.items():
                dir_errors = self._get_ref_errors("data", schema, path)
                if dir_errors:
                    """
                    TODO: there's an issue here (and any other places setting a key
                    that might be long) where the YAML dumper converts this to a
                    complex key and adds a ? at the front and inserts a line break
                    at the next instance of whitespace (in this case, leading
                    (as x) to be on a following line)
                    Wrote validation_utils > print_path to try to address this
                    issue, but needed to deprioritize.
                    """
                    errors.update(dir_errors)
        return errors

    def _validate(
        self,
        tsv_path: str,
        schema_version: SchemaVersion,
        report_type: ReportType = ReportType.STR,
    ) -> Dict[str, Any]:
        errors: Dict[str, Any] = {}
        local_validated = {}
        api_validated = {}
        if not schema_version.is_cedar:
            logging.info(
                f"""TSV {tsv_path} does not contain a metadata_schema_id,
                sending for local validation"""
            )
            try:
                schema = get_table_schema(
                    schema_version,
                    self.optional_fields,
                    self.offline,
                )
            except Exception as e:
                return {f"{tsv_path} (as {schema_version.table_schema})": e}

            if schema.get("deprecated") and not self.ignore_deprecation:
                return {"Schema version is deprecated": f"{schema_version.table_schema}"}

            local_errors = get_table_errors(tsv_path, schema, report_type)
            if local_errors:
                local_validated[f"{tsv_path} (as {schema_version.table_schema})"] = local_errors
        else:
            """
            Passing offline=True will skip all API/URL validation;
            GitHub actions therefore do not test via the CEDAR
            Spreadsheet Validator API, so tests must be run
            manually (see tests-manual/README.md)
            """
            if self.offline:
                logging.info(f"{tsv_path}: Offline validation selected, cannot reach API.")
                return errors
            else:
                api_errors = self.online_checks(tsv_path, schema_version, report_type)
                if api_errors:
                    api_validated[f"{tsv_path}"] = api_errors
        if local_validated:
            errors["Local Validation Errors"] = local_validated
        if api_validated:
            errors["CEDAR Validation Errors"] = api_validated
        return errors

    def online_checks(
        self,
        tsv_path: str,
        schema: SchemaVersion,
        report_type: ReportType = ReportType.STR,
    ) -> Optional[Dict]:
        url_errors = self._url_checks(tsv_path, schema, report_type)
        api_errors = self._api_validation(Path(tsv_path), report_type)
        if url_errors or api_errors:
            return url_errors | api_errors

    def _get_reference_errors(self) -> dict:
        errors: Dict[str, Any] = {}
        no_ref_errors = self.__get_no_ref_errors()
        multi_ref_errors = self.__get_multi_ref_errors()
        shared_dir_errors = self.__get_shared_dir_errors()
        if no_ref_errors:
            errors["No References"] = no_ref_errors
        if multi_ref_errors:
            errors["Multiple References"] = multi_ref_errors
        if shared_dir_errors:
            errors["Shared Directory References"] = shared_dir_errors
        return errors

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
                        errors[k].append(v)
            except PluginValidatorError as e:
                # We are ok with just returning a single error, rather than all.
                errors["Unexpected Plugin Error"] = [e]
        for k, v in errors.items():
            errors[k] = sorted(v)
        return dict(errors)  # get rid of defaultdict

    def _api_validation(
        self,
        tsv_path: Path,
        report_type: ReportType,
    ):
        errors = {}
        response = self._cedar_api_call(tsv_path)
        if response.status_code != 200:
            errors["Request Errors"] = response.json()
        elif response.json()["reporting"] and len(response.json()["reporting"]) > 0:
            errors["Validation Errors"] = [
                self._get_message(error, report_type) for error in response.json()["reporting"]
            ]
        else:
            logging.info(f"No errors found during CEDAR validation for {tsv_path}!")
        return errors

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
                f"Upload contains multiple parent multi-assay types: {multi_assay_parents}"
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
            self._check_multi_assay_children()
            self._check_data_paths_shared_with_parent()
            logging.info(f"Multi-assay parent: {self.multi_parent.dataset_type}")
            logging.info(
                f"Multi-assay components: {', '.join([component.dataset_type for component in self.multi_components])}"  # noqa: E501
            )
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
            message += f"Multi-assay parent type {self.multi_parent.dataset_type} missing required component(s) {necessary}."  # noqa: E501
        if not_allowed:
            message += f" Invalid child assay type(s) for parent type {self.multi_parent.dataset_type}: {not_allowed}"  # noqa: E501
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
                    f"Path(s) in {component.dataset_type} metadata TSV not present in parent: {unique_in_component}."  # noqa: E501
                )
            unique_in_parent = set(self.multi_assay_data_paths).difference(component_paths)
            if unique_in_parent:
                errors.append(
                    f"Path(s) in {self.multi_parent.dataset_type} metadata TSV not present in component {component.dataset_type}: {unique_in_parent}."  # noqa: E501
                )
        if errors:
            raise PreflightError(" ".join(error for error in errors))

    ##############################
    #
    # Supporting private methods:
    #
    ##############################

    def _cedar_api_call(self, tsv_path: Union[str, Path]) -> requests.models.Response:
        file = {"input_file": open(tsv_path, "rb")}
        headers = {"content_type": "multipart/form-data"}
        try:
            response = requests.post(
                "https://api.metadatavalidator.metadatacenter.org/service/validate-tsv",
                headers=headers,
                files=file,
            )
        except Exception as e:
            raise Exception(f"CEDAR API request for {tsv_path} failed! Exception: {e}")
        return response

    def _url_checks(
        self, tsv_path: str, schema: SchemaVersion, report_type: ReportType = ReportType.STR
    ):
        """
        Check provided values for parent_sample_id and orcid_id; additionally
        check sample_id, organ_id, and source_id values in single TSV validation
        via validation_utils.get_tsv_errors.
        """
        errors: Dict = {}

        # assay -> parent_sample_id
        # sample -> sample_id
        # organ -> organ_id
        # contributors -> orcid (new) / orcid_id (old)

        constrained_fields = {}
        schema_name = schema.schema_name

        if "sample" in schema_name:
            constrained_fields["sample_id"] = self.app_context.get("entities_url")
        elif "organ" in schema_name:
            constrained_fields["organ_id"] = self.app_context.get("entities_url")
        elif "murine-source" in schema_name:
            constrained_fields["source_id"] = self.app_context.get("entities_url")
        elif "contributors" in schema_name:
            if schema.is_cedar:
                constrained_fields["orcid"] = "https://orcid.org/"
            else:
                constrained_fields["orcid_id"] = "https://orcid.org/"
        else:
            constrained_fields["parent_sample_id"] = self.app_context.get("entities_url")

        url_errors = self._check_matching_urls(tsv_path, constrained_fields, report_type)
        if url_errors:
            errors["URL Errors"] = url_errors
        return errors

    def _check_matching_urls(
        self, tsv_path: str, constrained_fields: dict, report_type: ReportType = ReportType.STR
    ):
        rows = read_rows(Path(tsv_path), self.encoding)
        fields = rows[0].keys()
        missing_fields = [k for k in constrained_fields.keys() if k not in fields].sort()
        if missing_fields:
            return {f"Missing fields: {sorted(missing_fields)}"}
        if not self.globus_token:
            return {"No token": "No token was received to check URL fields against Entity API."}
        url_errors = []
        for i, row in enumerate(rows):
            check = {k: v for k, v in row.items() if k in constrained_fields}
            for field, value in check.items():
                if field == "parent_sample_id":
                    ids = value.split(",")
                    for id in ids:
                        error = self._check_single_url(field, id.strip(), constrained_fields, i)
                        if error:
                            url_errors.append(self._get_message(error, report_type))
                else:
                    error = self._check_single_url(field, value, constrained_fields, i)
                    if error:
                        url_errors.append(self._get_message(error, report_type))
        return url_errors

    def _check_single_url(
        self,
        field: str,
        value: str,
        constrained_fields: Dict[str, str],
        row_num: int,
    ) -> Optional[Dict]:
        try:
            url = constrained_fields[field] + value
            if field != "orcid_id":
                headers = self.app_context.get("request_header", {})
                headers["Authorization"] = f"Bearer {self.globus_token}"
            else:
                headers = {}
            response = requests.get(url, headers=headers)
            response.raise_for_status()
        except Exception as e:
            error = {
                "errorType": type(e).__name__,
                "column": field,
                "row": row_num + 2,
                "value": value,
                "error_text": e.__str__(),
            }
            return error

    def _get_message(
        self,
        error: Dict[str, str],
        report_type: ReportType = ReportType.STR,
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

        return_str = report_type is ReportType.STR
        if "errorType" in error and "column" in error and "row" in error and "value" in error:
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
    ) -> Optional[Dict]:
        if ref == "data":
            errors = self._check_data_path(schema_version, Path(metadata_path), path_value)
        else:
            errors = self._check_other_path(Path(metadata_path), path_value, ref)
        return errors

    def _get_ref_errors(
        self,
        ref: str,
        schema: SchemaVersion,
        metadata_path: Union[str, Path],
    ):
        ref_errors: DefaultDict[str, list] = defaultdict(list)
        # We don't want to continuously validate shared paths, e.g. contributors.tsv,
        # so this ensures we only check unique paths in a single metadata TSV once
        unique_paths = set()
        for row in schema.rows:
            field = f"{ref}_path"
            if not row.get(field):
                continue
            unique_paths.add(row[field])
        if ref == "contributors":
            schema.contributors_paths = [
                str(Path(Path(metadata_path).parent, path)) for path in unique_paths
            ]
        elif ref == "antibodies":
            schema.antibodies_paths = [
                str(Path(Path(metadata_path).parent, path)) for path in unique_paths
            ]
        for path_value in sorted(unique_paths):
            ref_error = self._check_path(path_value, ref, schema, metadata_path)
            if ref_error:
                ref_errors.update(ref_error)
        return ref_errors

    def _check_data_path(
        self, schema_version: SchemaVersion, metadata_path: Path, path_value: str
    ):
        data_path = Path(path_value)
        errors = {}

        if not schema_version.dir_schema:
            raise Exception(
                f"No directory schema found for data_path "
                f"{self.directory_path / data_path} in {metadata_path}!"
            )

        try:
            ref_errors = get_data_dir_errors(
                schema_version.dir_schema,
                root_path=self.directory_path,
                data_dir_path=data_path,
                dataset_ignore_globs=self.dataset_ignore_globs,
            ).popitem()
            if type(ref_errors[1]) is list:
                errors[
                    f"{str(metadata_path)}, column 'data_path', value '{path_value}' (as {ref_errors[0]})"
                ] = ref_errors[1]
            schema_version.dir_schema = ref_errors[0]
        except Exception as e:
            errors[f"{str(metadata_path)}, column 'data_path', value '{path_value}'"] = e
        return errors

    def _check_other_path(self, metadata_path: Path, other_path_value: str, path_type: str):
        errors = {}
        other_path = self.directory_path / other_path_value
        try:
            schema = get_schema_version(
                other_path,
                self.encoding,
                self.app_context["ingest_url"],
                self.directory_path,
                offline=self.offline,
            )
        except Exception as e:
            errors[f"{metadata_path}, column '{path_type}_path', value '{other_path_value}'"] = [e]
            return errors
        tsv_ref_errors = self.validation_routine(tsv_paths={str(other_path): schema})
        # TSV located and read, errors found
        if tsv_ref_errors and isinstance(tsv_ref_errors, list):
            errors[other_path] = tsv_ref_errors
        # Problem with TSV
        elif tsv_ref_errors and isinstance(tsv_ref_errors, dict):
            errors[
                f"{str(metadata_path)}, column '{path_type}_path', value '{other_path_value}'"
            ] = tsv_ref_errors
        return errors

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
        return references
