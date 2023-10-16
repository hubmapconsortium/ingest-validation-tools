from __future__ import annotations
import logging

import subprocess
from collections import Counter, defaultdict
from datetime import datetime
from fnmatch import fnmatch
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, DefaultDict

import requests
from requests.auth import HTTPBasicAuth

from ingest_validation_tools.plugin_validator import (
    ValidatorError as PluginValidatorError,
)
from ingest_validation_tools.plugin_validator import run_plugin_validators_iter
from ingest_validation_tools.schema_loader import (
    PreflightError,
    SchemaVersion,
)
from ingest_validation_tools.table_validator import ReportType
from ingest_validation_tools.validation_utils import (
    dict_reader_wrapper,
    get_context_of_decode_error,
    get_data_dir_errors,
    get_directory_schema_versions,
    get_json,
    get_other_names,
    get_table_schema_version,
    get_tsv_errors,
)

TSV_SUFFIX = "metadata.tsv"


class ErrorDictException(Exception):
    def __init__(self, errors):
        message = f"Halting compilation of errors after detecting the following errors: {errors}."
        super().__init__(message)
        # This returns only the error that caused the exception.
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
        token: str = "",
        cedar_api_key: str = "",
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
        self.auth_tok = token
        self.cedar_api_key = cedar_api_key

        try:
            unsorted_effective_tsv_paths = {
                str(path): get_table_schema_version(path, self.encoding)
                for path in (
                    tsv_paths if tsv_paths else directory_path.glob(f"*{TSV_SUFFIX}")
                )
            }
            self.effective_tsv_paths = {
                k: unsorted_effective_tsv_paths[k]
                for k in sorted(unsorted_effective_tsv_paths.keys())
            }
        except PreflightError as e:
            self.errors["Preflight"] = str(e)

    #####################
    #
    # Two public methods:
    #
    #####################

    def get_info(self) -> dict:
        git_version = subprocess.check_output(
            "git rev-parse --short HEAD".split(" "),
            encoding="ascii",
            stderr=subprocess.STDOUT,
        ).strip()

        try:
            effective_tsvs = {
                Path(path).name: {
                    "Schema": sv.schema_name,
                    "Metadata schema version": sv.version,
                    "Directory schema versions": get_directory_schema_versions(
                        path, sv.version, encoding="ascii"
                    ),
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
            self.errors["Preflight"] = str(e)
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
            other_errors = self.check_other_schemas()
            if other_errors and not self.effective_tsv_paths:
                return other_errors
            elif self.effective_tsv_paths:
                errors.update(other_errors)
            else:
                return {}

            upload_errors = self.check_upload()
            if upload_errors:
                errors["Upload Errors"] = upload_errors

            validation_errors = self.validation_routine()
            if validation_errors:
                errors["Metadata TSV Validation Errors"] = validation_errors

            reference_errors = self._get_reference_errors()
            if reference_errors:
                errors["Reference Errors"] = reference_errors

            plugin_errors = self._get_plugin_errors(**kwargs)
            if plugin_errors:
                errors["Plugin Errors"] = plugin_errors
        except ErrorDictException as e:
            return errors | e.errors

        return errors

    ###################################
    #
    # Top-level private methods:
    #
    ###################################

    def check_other_schemas(self):
        errors = {}
        others = get_other_names()
        # Antibodies and contributors are handled elsewhere
        others.remove("antibodies")
        others.remove("contributors")
        for tsv_path, schema_version in self.effective_tsv_paths.items():
            if schema_version.schema_name in others:
                error = self._validate(tsv_path, schema_version)
                if error:
                    errors[f"{tsv_path} (as {schema_version.schema_name})"] = error
        self.effective_tsv_paths = {
            k: v
            for k, v in self.effective_tsv_paths.items()
            if v.schema_name not in others
        }
        return errors

    def check_upload(self) -> dict:
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
        types_counter = Counter(
            [v.schema_name for v in self.effective_tsv_paths.values()]
        )
        repeated = [
            assay_type for assay_type, count in types_counter.items() if count > 1
        ]
        if repeated:
            raise ErrorDictException(
                {
                    "Repeated": f"There is more than one TSV for this type: {', '.join(repeated)}"
                }
            )
        for path, schema_version in self.effective_tsv_paths.items():
            schema_name = schema_version.schema_name
            rows = self._get_rows_from_tsv(path)
            if not isinstance(rows, list):
                return {f"{path} (as {schema_name})": rows}
            for ref in ["contributors", "antibodies"]:
                ref_errors = self._get_ref_errors(rows, ref, schema_version, path)
                if ref_errors:
                    errors.update(ref_errors)
        return errors

    def _get_directory_errors(self) -> dict:
        errors = {}
        for path, schema_version in self.effective_tsv_paths.items():
            schema_name = schema_version.schema_name
            rows = self._get_rows_from_tsv(path)
            if not isinstance(rows, list):
                return {f"{path} (as {schema_name})": rows}
            if "data_path" not in rows[0] or "contributors_path" not in rows[0]:
                errors[
                    "Path Errors"
                ] = "File is missing data_path or contributors_path."
            else:
                dir_errors = self._get_ref_errors(rows, "data", schema_version, path)
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

    def validation_routine(self) -> dict:
        errors: DefaultDict[str, dict] = defaultdict(dict)
        for tsv_path, schema_version in self.effective_tsv_paths.items():
            path_errors = self._validate(tsv_path, schema_version)
            if path_errors:
                for key, value in path_errors.items():
                    errors[key].update(value)
        return errors

    def _validate(
        self,
        tsv_path: str,
        schema_version: SchemaVersion,
    ) -> Dict[str, Any]:
        errors: Dict[str, Any] = {}
        local_validated = {}
        api_validated = {}
        rows = self._get_rows_from_tsv(tsv_path)
        if isinstance(rows, dict):
            return rows
        if "metadata_schema_id" not in rows[0].keys():
            logging.info(
                f"""TSV {tsv_path} does not contain a metadata_schema_id,
                sending for local validation"""
            )
            local_errors = self.__get_assay_tsv_errors(
                schema_version.schema_name, Path(tsv_path)
            )
            if local_errors:
                local_validated[
                    f"{tsv_path} (as {schema_version.schema_name}-v{schema_version.version})"
                ] = local_errors
        else:
            if self.offline:
                api_validated = {
                    f"{tsv_path}": "Offline validation selected, cannot reach API."
                }
            else:
                url_errors = self._cedar_url_checks(tsv_path, schema_version)
                api_errors = self.api_validation(Path(tsv_path))
                if url_errors or api_errors:
                    api_validated[f"{tsv_path}"] = url_errors | api_errors
        if local_validated:
            errors["Local Validation Errors"] = local_validated
        if api_validated:
            errors["CEDAR Validation Errors"] = api_validated
        return errors

    def _get_reference_errors(self) -> dict:
        errors: Dict[str, Any] = {}
        no_ref_errors = self.__get_no_ref_errors()
        try:
            multi_ref_errors = self.__get_multi_ref_errors()
            if no_ref_errors:
                errors["No References"] = no_ref_errors
            if multi_ref_errors:
                errors["Multiple References"] = multi_ref_errors
        except UnicodeDecodeError as e:
            errors["Decode Error"] = get_context_of_decode_error(e)
        return errors

    def _get_plugin_errors(self, **kwargs) -> dict:
        plugin_path = self.plugin_directory
        if not plugin_path:
            return {}
        errors: DefaultDict[str, list] = defaultdict(list)
        for metadata_path in self.effective_tsv_paths.keys():
            try:
                for k, v in run_plugin_validators_iter(
                    metadata_path, plugin_path, **kwargs
                ):
                    errors[k].append(v)
            except PluginValidatorError as e:
                # We are ok with just returning a single error, rather than all.
                errors["Unexpected Plugin Error"] = [e]
        return dict(errors)  # get rid of defaultdict

    def api_validation(self, tsv_path: Path, report_type: ReportType = ReportType.STR):
        errors = {}
        if not self.cedar_api_key:
            return {
                "Request Errors": f"No CEDAR API key passed, cannot validate {tsv_path}!"
            }
        response = self._cedar_api_call(tsv_path)
        if response.status_code != 200:
            errors["Request Errors"] = response.json()
        elif response.json()["reporting"] and len(response.json()["reporting"]) > 0:
            errors["Validation Errors"] = [
                self._get_message(error, report_type)
                for error in response.json()["reporting"]
            ]
        else:
            logging.info(f"No errors found during CEDAR validation for {tsv_path}!")
        return errors

    ##############################
    #
    # Supporting private methods:
    #
    ##############################

    def _cedar_api_call(self, tsv_path: Union[str, Path]) -> requests.models.Response:
        auth = HTTPBasicAuth("apikey", self.cedar_api_key)
        file = {"input_file": open(tsv_path, "rb")}
        headers = {"content_type": "multipart/form-data"}
        try:
            response = requests.post(
                "https://api.metadatavalidator.metadatacenter.org/service/validate-tsv",
                auth=auth,
                headers=headers,
                files=file,
            )
        except Exception as e:
            raise Exception(f"CEDAR API request for {tsv_path} failed! Exception: {e}")
        return response

    def _cedar_url_checks(self, tsv_path: str, schema_version: SchemaVersion):
        """
        Check provided UUIDs/HuBMAP IDs for parent_id, sample_id, organ_id.
        Not using get_table_errors because CEDAR schema fields do not match
        the TSV fields, which makes frictionless confused and upset.
        """
        errors: Dict = {}

        # assay -> parent_sample_id
        # sample -> sample_id
        # organ -> organ_id
        # contributors -> orcid_id

        constrained_fields = {}
        schema_name = schema_version.schema_name

        if "sample" in schema_name:
            constrained_fields['sample_id'] = "https://entity.api.hubmapconsortium.org/entities/"
        elif "organ" in schema_name:
            constrained_fields['organ_id'] = "https://entity.api.hubmapconsortium.org/entities/"
        elif "contributors" in schema_name:
            constrained_fields['orcid_id'] = "https://pub.orcid.org/v3.0/"
        else:
            constrained_fields['parent_sample_id'] = \
                "https://entity.api.hubmapconsortium.org/entities/"

        url_errors = self._check_matching_urls(tsv_path, constrained_fields)
        if url_errors:
            errors["URL Errors"] = url_errors
        return errors

    def _check_matching_urls(self, tsv_path: str, constrained_fields: dict):
        rows = self._get_rows_from_tsv(tsv_path)
        if isinstance(rows, dict):
            return rows
        fields = rows[0].keys()
        missing_fields = [k for k in constrained_fields.keys() if k not in fields]
        if missing_fields:
            return {f"Missing fields: {missing_fields}"}
        # TODO: not sure if a token is our best bet here; will all UUID/HMID
        # fields be accessible via the portal?
        if not self.auth_tok:
            return {
                "No token": "No token was received to check URL fields against Entity API."
            }
        url_errors = []
        for i, row in enumerate(rows):
            check = {k: v for k, v in row.items() if k in constrained_fields}
            for field, url in check.items():
                try:
                    url = constrained_fields[field] + url
                    response = requests.get(
                        url,
                        headers={
                            "X-Hubmap-Application": "ingest-pipeline",
                            "Authorization": f"Bearer {self.auth_tok}",
                        },
                    )
                    response.raise_for_status()
                except Exception as e:
                    url_errors.append(
                        f"Row {i+2}, field '{field}' with value '{url}': {e}"
                    )
        return url_errors

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

        return_str = report_type is ReportType.STR
        if (
            "errorType" in error
            and "column" in error
            and "row" in error
            and "value" in error
        ):
            # This may need readability improvements
            msg = (
                f'On row {error["row"]}, column "{error["column"]}", '
                f'value "{error["value"]}" fails because of error "{error["errorType"]}"'
                f'{f". Example: {example}" if example else example}'
            )
            return msg if return_str else get_json(msg, error["row"], error["column"])
        return error

    def _get_rows_from_tsv(self, path: Union[str, Path]) -> Union[Dict, List]:
        errors = {}
        try:
            rows = dict_reader_wrapper(path, self.encoding)
            return rows
        except UnicodeDecodeError as e:
            errors["Decode Errors"] = get_context_of_decode_error(e)
        except IsADirectoryError:
            errors["Path Errors"] = f"Expected a TSV, found a directory at {path}."
        return errors

    def _check_path(
        self,
        i: int,
        path: Path,
        ref: str,
        schema_name: str,
        schema_version: str,
        metadata_path: Union[str, Path],
    ) -> Optional[Dict]:
        errors: Dict[
            str, Union[list, dict]
        ] = {}  # This is very ugly but makes mypy happy
        if ref == "data":
            ref_errors = get_data_dir_errors(
                schema_name,
                path,
                schema_version,
                dataset_ignore_globs=self.dataset_ignore_globs,
            )
            if ref_errors:
                # TODO: quote field name to match TSV error output;
                # will break tests
                errors[f"{metadata_path}, row {i+2}, column {ref}_path"] = ref_errors
        else:
            tsv_ref_errors = get_tsv_errors(
                schema_name=ref,
                tsv_path=path,
                offline=self.offline,
                encoding=self.encoding,
                ignore_deprecation=self.ignore_deprecation,
                cedar_api_key=self.cedar_api_key
            )
            # TSV located and read, errors found
            if tsv_ref_errors and isinstance(tsv_ref_errors, list):
                errors[f"{path}"] = tsv_ref_errors
            # Problem with TSV
            elif tsv_ref_errors and isinstance(tsv_ref_errors, dict):
                errors[
                    f"{metadata_path} row {i+2}, column '{ref}_path'"
                ] = tsv_ref_errors
        return errors

    def __get_assay_tsv_errors(self, assay_type: str, path: Path):
        return get_tsv_errors(
            schema_name=assay_type,
            tsv_path=path,
            offline=self.offline,
            encoding=self.encoding,
            optional_fields=self.optional_fields,
            ignore_deprecation=self.ignore_deprecation,
        )

    def _get_ref_errors(
        self,
        rows: list,
        ref: str,
        schema: SchemaVersion,
        metadata_path: Union[str, Path],
    ):
        ref_errors: DefaultDict[str, list] = defaultdict(list)
        for i, row in enumerate(rows):
            field = f"{ref}_path"
            if not row.get(field):
                continue
            data_path = self.directory_path / row[field]
            ref_error = self._check_path(
                i,
                data_path,
                ref,
                schema.schema_name,
                schema.version,
                metadata_path,
            )
            if ref_error:
                ref_errors.update(ref_error)
        return ref_errors

    def __get_no_ref_errors(self) -> dict:
        referenced_data_paths = (
            set(self.__get_data_references().keys())
            | set(self.__get_contributors_references().keys())
            | set(self.__get_antibodies_references().keys())
        )

        referenced_data_paths = {
            Path(path) for path in referenced_data_paths
        }

        non_metadata_paths = {
            Path(path.name)
            for path in self.directory_path.iterdir()
            if not path.name.endswith(TSV_SUFFIX)
            and not any([fnmatch(path.name, glob) for glob in self.upload_ignore_globs])
        }
        unreferenced_paths = non_metadata_paths - referenced_data_paths
        unreferenced_dir_paths = [
            path for path in unreferenced_paths if Path(path).is_dir()
        ]
        unreferenced_file_paths = [
            path for path in unreferenced_paths if not Path(path).is_dir()
        ]
        errors = {}
        if unreferenced_dir_paths:
            errors["Directories"] = unreferenced_dir_paths
        if unreferenced_file_paths:
            errors["Files"] = unreferenced_file_paths
        return errors

    def __get_multi_ref_errors(self) -> dict:
        # TODO: This needs to be updated to include multi-assay logic
        #  If - multi-assay dataset (and only that dataset is referenced) don't fail
        #  Else - fail
        errors = {}
        data_references = self.__get_data_references()
        for path, references in data_references.items():
            if len(references) > 1:
                errors[path] = references
        return errors

    def __get_data_references(self) -> dict:
        return self.__get_references("data_path")

    def __get_antibodies_references(self) -> dict:
        return self.__get_references("antibodies_path")

    def __get_contributors_references(self) -> dict:
        return self.__get_references("contributors_path")

    def __get_references(self, col_name) -> dict:
        references = defaultdict(list)
        for tsv_path in self.effective_tsv_paths.keys():
            for i, row in enumerate(dict_reader_wrapper(tsv_path, self.encoding)):
                if col_name in row:
                    reference = f"{tsv_path} (row {i+2})"
                    references[row[col_name]].append(reference)
        return references
