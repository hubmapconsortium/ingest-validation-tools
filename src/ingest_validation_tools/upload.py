from __future__ import annotations
import logging

import subprocess
from collections import Counter, defaultdict
from datetime import datetime
from fnmatch import fnmatch
from pathlib import Path
from typing import Any, Dict, Optional, Union, DefaultDict

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
        run_plugins: bool = False,
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

        try:
            unsorted_effective_tsv_paths = {
                str(path): get_schema_version(
                    path,
                    self.encoding,
                    self.globus_token,
                    self.directory_path,
                )
                for path in (
                    tsv_paths if tsv_paths else directory_path.glob(f"*{TSV_SUFFIX}")
                )
            }

            self.effective_tsv_paths = {
                k: unsorted_effective_tsv_paths[k]
                for k in sorted(unsorted_effective_tsv_paths.keys())
            }

            self.multi_assay_structure = self._check_multi_assay()

        except PreflightError as e:
            self.errors["Preflight"] = e

    #####################
    #
    # Public methods:
    #
    #####################

    def get_info(self) -> dict:
        git_version = subprocess.check_output(
            "git rev-parse --short HEAD".split(" "),
            encoding="ascii",
            stderr=subprocess.STDOUT,
        ).strip()

        try:
            # TODO: this previously returned a list of dir schema versions;
            # it has been converted to return a single dir_schema filename--
            # is this problematic for any reason?
            effective_tsvs = {
                Path(path).name: {
                    "Schema": sv.table_schema,
                    "Metadata schema version": sv.version,
                    "Directory schema versions": sv.dir_schema,
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

    # TODO: simplify/refactor
    def _check_multi_assay(self) -> Dict[str, Dict]:
        # This is not recursive, so if there are nested multi-assay types it will not work
        # TODO: "name" value is a list even though there can only be one because typing
        # was being annoying
        shared_data_paths = defaultdict(lambda: defaultdict(list))
        multi_assay_parents = [
            sv for sv in self.effective_tsv_paths.values() if sv.contains
        ]
        if len(multi_assay_parents) == 0:
            return {}
        components = [sv for sv in self.effective_tsv_paths.values() if not sv.contains]
        if len(multi_assay_parents) > 1:
            raise PreflightError(
                f"Upload contains multiple parent multi-assay types: {multi_assay_parents}"
            )
        parent = multi_assay_parents[0]
        not_allowed = []
        # Iterate through child dataset types, check that they are valid
        # components of parent multi-assay type
        for sv in components:
            if sv.dataset_type.lower() not in parent.contains:
                not_allowed.append(sv.dataset_type)
            for row in sv.rows:
                if row.get("data_path"):
                    shared_data_paths[row["data_path"]]["components"].append(sv)
        if not_allowed:
            raise PreflightError(
                f"Invalid child assay type(s) for parent type {parent.dataset_type}: {not_allowed}"
            )
        # Check parent multi-assay TSV data_path values against data_paths in child TSVs
        multi_data_paths = [row.get("data_path") for row in parent.rows]
        for path, related_svs in shared_data_paths.items():
            # If component dataset types are missing from parent must_contain list
            # for a given data_path, error
            if sorted(
                [sv.dataset_type.lower() for sv in related_svs["components"]]
            ) != sorted(parent.contains):
                raise PreflightError(
                    f"Multi-assay type '{parent.dataset_type}' requires {parent.contains} but only components {[c.dataset_type for c in components]} share the data path {path}."  # noqa: 501
                )
            # If paths match between parent and components and all required components
            # are present, add parent dataset type to shared_data_paths, remove path
            # from multi_data_paths, and continue
            # This will also potentially create data path values in the dict without a "parent"
            # key, indicating a standalone dataset of a child type (for dir and ref checking)
            shared_data_paths[path]["parent"] = [parent]
            multi_data_paths.remove(path)
        # If a unique path is found in the parent TSV, error
        if multi_data_paths:
            raise PreflightError(
                f"""
                Multi-assay TSV {parent.path} contains data paths that are not present
                in child assay TSVs. Data paths unique to parent: {multi_data_paths}
                """
            )
        converted_data_paths = {}
        for path, related_sv in shared_data_paths.items():
            if related_sv.get("parent"):
                shared_data_paths[path]["parent"] = shared_data_paths[path]["parent"][0]
            converted_data_paths[path] = dict(related_sv)
        return converted_data_paths

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
        for path, schema in self.effective_tsv_paths.items():
            if (
                "data_path" not in schema.rows[0]
                or "contributors_path" not in schema.rows[0]
            ):
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
        if self.multi_assay_structure:
            for path, dataset_types in self.multi_assay_structure.items():
                dir_errors = self._get_multi_assay_dir_errors(path, dataset_types)
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

    def _get_multi_assay_dir_errors(
        self, path: str, dataset_types: Dict
    ) -> Optional[Dict]:
        data_path = self.directory_path / path
        parent = dataset_types.get("parent")
        # Validate against parent multi-assay type if data_path is in parent TSV
        if parent:
            return self._multi_assay_dir_check(parent, data_path, path)
        # Validate against component structure otherwise
        elif dataset_types.get("components"):
            errors = {}
            for component in dataset_types["components"]:
                errors.update(self._multi_assay_dir_check(component, data_path, path))
            return errors

    def _multi_assay_dir_check(
        self, schema: SchemaVersion, ref_path: Path, data_path: str
    ) -> Dict:
        errors = {}
        if not schema.dir_schema:
            raise Exception(
                f"No directory schema found for data_path {ref_path} in {schema.path}!"
            )
        ref_errors = get_data_dir_errors(
            schema.dir_schema,
            ref_path,
            dataset_ignore_globs=self.dataset_ignore_globs,
        )
        if ref_errors:
            errors[f"{schema.path}, column 'data_path', value {data_path}"] = ref_errors
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
                return {
                    "Schema version is deprecated": f"{schema_version.table_schema}"
                }

            local_errors = get_table_errors(tsv_path, schema, report_type)
            if local_errors:
                local_validated[
                    f"{tsv_path} (as {schema_version.table_schema})"
                ] = local_errors
        else:
            """
            Passing offline=True will skip all API/URL validation;
            GitHub actions therefore do not test via the CEDAR
            Spreadsheet Validator API, so tests must be run
            manually (see tests-manual/README.md)
            """
            if self.offline:
                logging.info(
                    f"{tsv_path}: Offline validation selected, cannot reach API."
                )
                return errors
            else:
                url_errors = self._cedar_url_checks(tsv_path, schema_version)
                api_errors = self._api_validation(Path(tsv_path), report_type)
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
        multi_ref_errors = self.__get_multi_ref_errors()
        if no_ref_errors:
            errors["No References"] = no_ref_errors
        if multi_ref_errors:
            errors["Multiple References"] = multi_ref_errors
        return errors

    def _get_plugin_errors(self, **kwargs) -> dict:
        # TODO: needs to be updated to use canonical assay names;
        # requires a look into ingest-validation-tests as well
        plugin_path = self.plugin_directory
        if not plugin_path:
            return {}
        errors: DefaultDict[str, list] = defaultdict(list)
        for metadata_path, sv in self.effective_tsv_paths.items():
            try:
                for k, v in run_plugin_validators_iter(
                    metadata_path, sv, plugin_path, **kwargs
                ):
                    errors[k].append(v)
            except PluginValidatorError as e:
                # We are ok with just returning a single error, rather than all.
                errors["Unexpected Plugin Error"] = [e]
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
            constrained_fields[
                "sample_id"
            ] = "https://entity.api.hubmapconsortium.org/entities/"
        elif "organ" in schema_name:
            constrained_fields[
                "organ_id"
            ] = "https://entity.api.hubmapconsortium.org/entities/"
        elif "contributors" in schema_name:
            constrained_fields["orcid_id"] = "https://pub.orcid.org/v3.0/"
        else:
            constrained_fields[
                "parent_sample_id"
            ] = "https://entity.api.hubmapconsortium.org/entities/"

        url_errors = self._check_matching_urls(tsv_path, constrained_fields)
        if url_errors:
            errors["URL Errors"] = url_errors
        return errors

    def _check_matching_urls(self, tsv_path: str, constrained_fields: dict):
        rows = read_rows(Path(tsv_path), "ascii")
        fields = rows[0].keys()
        missing_fields = [
            k for k in constrained_fields.keys() if k not in fields
        ].sort()
        if missing_fields:
            return {f"Missing fields: {sorted(missing_fields)}"}
        if not self.globus_token:
            return {
                "No token": "No token was received to check URL fields against Entity API."
            }
        url_errors = []
        for i, row in enumerate(rows):
            check = {k: v for k, v in row.items() if k in constrained_fields}
            for field, value in check.items():
                try:
                    url = constrained_fields[field] + value
                    response = requests.get(
                        url,
                        headers={
                            "X-Hubmap-Application": "ingest-pipeline",
                            "Authorization": f"Bearer {self.globus_token}",
                        },
                    )
                    response.raise_for_status()
                except Exception as e:
                    url_errors.append(
                        f"Row {i+2}, field '{field}' with value '{value}': {e}"
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

    def _check_path(
        self,
        i: int,
        path: Path,
        ref: str,
        schema_version: SchemaVersion,
        metadata_path: Union[str, Path],
    ) -> Optional[Dict]:
        # TODO: it's weird that this method does two wildly different things; fix
        errors: Dict[
            str, Union[list, dict]
        ] = {}  # This is very ugly but makes mypy happy
        if ref == "data":
            if not schema_version.dir_schema:
                raise Exception(
                    f"No directory schema found for data_path {path} in {metadata_path}!"
                )
            ref_errors = get_data_dir_errors(
                schema_version.dir_schema,
                path,
                dataset_ignore_globs=self.dataset_ignore_globs,
            )
            if ref_errors:
                # TODO: quote field name to match TSV error output;
                # will break tests
                errors[f"{metadata_path}, row {i+2}, column {ref}_path"] = ref_errors
        # TODO: this is all to support other types, should probably be broken out
        else:
            try:
                schema = get_schema_version(
                    path,
                    self.encoding,
                    self.globus_token,
                    self.directory_path,
                )
            except Exception as e:
                errors[f"{str(metadata_path)}, row {i+2}, column '{ref}_path'"] = [e]
                return errors
            tsv_ref_errors = self.validation_routine(tsv_paths={str(path): schema})
            # TSV located and read, errors found
            if tsv_ref_errors and isinstance(tsv_ref_errors, list):
                errors[f"{path}"] = tsv_ref_errors
            # Problem with TSV
            elif tsv_ref_errors and isinstance(tsv_ref_errors, dict):
                errors[
                    f"{metadata_path} row {i+2}, column '{ref}_path'"
                ] = tsv_ref_errors
        return errors

    def _get_ref_errors(
        self,
        ref: str,
        schema: SchemaVersion,
        metadata_path: Union[str, Path],
    ):
        ref_errors: DefaultDict[str, list] = defaultdict(list)
        for i, row in enumerate(schema.rows):
            field = f"{ref}_path"
            if not row.get(field):
                continue
            ref_path = self.directory_path / row[field]
            # TODO: _check_path is really slamming the Metadata Validator API with the
            # contributors.tsv; gather unique values from contributors/antibodies
            # and validate once per?
            ref_error = self._check_path(i, ref_path, ref, schema, metadata_path)
            if ref_error:
                ref_errors.update(ref_error)
        return ref_errors

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
        #  If - multi-assay dataset (and only that dataset is referenced) don't fail
        #  Else - fail
        errors = {}
        data_references = self.__get_data_references()
        multi_references = [
            path
            for path, value in self.multi_assay_structure.items()
            if value.get("parent")
        ]
        for path, references in data_references.items():
            if path not in multi_references:
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
        for tsv_path, schema in self.effective_tsv_paths.items():
            for i, row in enumerate(schema.rows):
                if col_name in row:
                    reference = f"{tsv_path} (row {i+2})"
                    references[row[col_name]].append(reference)
        return references
