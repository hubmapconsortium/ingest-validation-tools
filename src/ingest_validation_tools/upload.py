from __future__ import annotations

import logging
import os

import subprocess
from collections import Counter, defaultdict
from datetime import datetime
from fnmatch import fnmatch
from pathlib import Path

import pandas as pd
import requests
from requests.auth import HTTPBasicAuth

from ingest_validation_tools.plugin_validator import (
    ValidatorError as PluginValidatorError,
)
from ingest_validation_tools.plugin_validator import run_plugin_validators_iter
from ingest_validation_tools.schema_loader import PreflightError, SchemaVersion
from ingest_validation_tools.validation_utils import (
    dict_reader_wrapper,
    get_context_of_decode_error,
    get_data_dir_errors,
    get_directory_schema_versions,
    get_table_schema_version,
    get_tsv_errors,
)

TSV_SUFFIX = "metadata.tsv"
API_KEY_SECRET = ""


class Upload:
    def __init__(
        self,
        directory_path=None,
        tsv_paths=[],
        optional_fields=[],
        add_notes=True,
        dataset_ignore_globs=[],
        upload_ignore_globs=[],
        plugin_directory=None,
        encoding: str = "utf-8",
        offline=None,
        ignore_deprecation=False,
        extra_parameters={},
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
        self.extra_parameters = extra_parameters
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

        effective_tsvs = {
            Path(path).name: {
                "Schema": sv.schema_name,
                "Metadata schema version": sv.version,
                "Directory schema versions": get_directory_schema_versions(
                    path, encoding="ascii"
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

    def get_errors(self, **kwargs) -> dict:
        # This creates a deeply nested dict.
        # Keys are present only if there is actually an error to report.
        # plugin_kwargs are passed to the plugin validators.

        kwargs.update(self.extra_parameters)
        if self.errors:
            return self.errors

        errors = {}

        tsv_errors = self._check_tsvs()
        if tsv_errors:
            errors["Metadata TSV Errors"] = tsv_errors

        dir_errors = self.get_directory_errors()
        if dir_errors:
            errors["Directory Errors"] = dir_errors

        validation_errors = self.validation_routine()
        if validation_errors:
            errors["Validation Errors"] = validation_errors

        reference_errors = self._get_reference_errors()
        if reference_errors:
            errors["Reference Errors"] = reference_errors

        plugin_errors = self._get_plugin_errors(**kwargs)
        if plugin_errors:
            errors["Plugin Errors"] = plugin_errors

        return errors

    def get_rows_from_tsv(self, path: str | Path) -> dict | list:
        errors = {}
        try:
            rows = dict_reader_wrapper(path, self.encoding)
            return rows
        except UnicodeDecodeError as e:
            errors["Decode Errors"] = get_context_of_decode_error(e)
        except IsADirectoryError:
            errors["Path Errors"] = f"Expected a TSV, found a directory at {path}."
        return errors

    def get_directory_errors(self) -> dict:
        errors = {}
        if not self.directory_path:
            return errors
        for path, schema_version in self.effective_tsv_paths.items():
            single_path_errors = {}
            schema_name = schema_version.schema_name
            # Doing some TSV parsing here to validate directory structure
            rows = self.get_rows_from_tsv(path)
            if type(rows) == dict:
                errors[f"{path} (as {schema_name})"] = rows
                continue
            elif "data_path" not in rows[0] or "contributors_path" not in rows[0]:
                single_path_errors[
                    "Path Errors"
                ] = "File is missing data_path or contributors_path."
            else:
                for i, row in enumerate(rows):
                    row_number = f"row {i+2}"
                    if not row.get("data_path"):
                        continue
                    path = self.directory_path / row["data_path"]
                    ref_errors = self.__get_ref_errors("data", path, schema_name)
                    if ref_errors:
                        single_path_errors[f"{row_number}, data {path}"] = ref_errors
            errors[f"{path} (as {schema_name})"] = single_path_errors
        return errors

    def cedar_api_call(self, tsv_path: str | Path) -> requests.Response:
        auth = HTTPBasicAuth("apikey", os.environ[API_KEY_SECRET])
        file = {"input_file": open(tsv_path, "rb")}
        try:
            response = requests.post(
                "https://api.metadatavalidator.metadatacenter.org/service/validate-tsv",
                auth=auth,
                files=file,
            )
        except Exception as e:
            raise Exception(f"CEDAR API request for {tsv_path} failed! Exception: {e}")
        return response

    def validation_routine(self) -> dict:
        errors = {}
        local_validated = {}
        api_validated = {}
        for tsv_path, schema_name in self.effective_tsv_paths.items():
            if not type(tsv_path) == Path:
                try:
                    tsv_path = Path(tsv_path)
                except TypeError as e:
                    raise TypeError(
                        f"Path {tsv_path} is of invalid type {type(tsv_path)}. Exception: {e}"
                    )
            df = pd.read_csv(tsv_path, delimiter="\t")
            if df.get(["metadata_schema_id"]) is None:
                logging.info(
                    f"""TSV {tsv_path} does not contain a metadata_schema_id,
                    sending for local validation"""
                )
                local_errors = self._get_tsv_errors(tsv_path, schema_name)
                if local_errors:
                    local_validated[tsv_path] = local_errors
            else:
                api_errors = self.api_validation(tsv_path)
                if api_errors:
                    api_validated[f"{tsv_path}"] = api_errors
        if local_validated:
            errors["Local Validation Errors"] = local_validated
        if api_validated:
            errors["CEDAR Validation Errors"] = api_validated
        return errors

    def api_validation(self, tsv_path: Path):
        errors = {}
        response = self.cedar_api_call(tsv_path)
        if response.status_code != 200:
            errors["Request Errors"] = response
        elif response.json()["reporting"] and len(response.json()["reporting"]) > 0:
            errors["Error Report"] = response.json()["reporting"]
        if errors:
            logging.info(f"CEDAR Spreadsheet Validator errors for {tsv_path}: {errors}")
        return errors

    ###################################
    #
    # Top-level private methods:
    #
    ###################################

    def _check_tsvs(self) -> dict | None:
        if not self.effective_tsv_paths:
            return {"Missing": "There are no effective TSVs."}

        types_counter = Counter(
            [v.schema_name for v in self.effective_tsv_paths.values()]
        )
        repeated = [
            assay_type for assay_type, count in types_counter.items() if count > 1
        ]
        if repeated:
            return {
                "Repeated": f'There is more than one TSV for this type: {", ".join(repeated)}'
            }

    def _get_tsv_errors(self, path: Path, schema_version: SchemaVersion) -> dict:
        errors = {}
        schema_name = schema_version.schema_name

        single_tsv_internal_errors = self.__get_assay_tsv_errors(schema_name, path)
        single_tsv_external_errors = self.__get_assay_reference_errors(
            schema_name, path
        )

        if single_tsv_internal_errors:
            errors["Internal"] = single_tsv_internal_errors
        if single_tsv_external_errors:
            errors["External"] = single_tsv_external_errors
        return errors

    def _get_reference_errors(self) -> dict:
        errors = {}
        no_ref_errors = self.__get_no_ref_errors()
        try:
            multi_ref_errors = self.__get_multi_ref_errors()
        except UnicodeDecodeError as e:
            return get_context_of_decode_error(e)
        if no_ref_errors:
            errors["No References"] = no_ref_errors
        if multi_ref_errors:
            errors["Multiple References"] = multi_ref_errors
        return errors

    def _get_plugin_errors(self, **kwargs) -> dict:
        plugin_path = self.plugin_directory
        if not plugin_path:
            return None
        errors = defaultdict(list)
        for metadata_path in self.effective_tsv_paths.keys():
            try:
                for k, v in run_plugin_validators_iter(
                    metadata_path, plugin_path, **kwargs
                ):
                    errors[k].append(v)
            except PluginValidatorError as e:
                # We are ok with just returning a single error, rather than all.
                errors["Unexpected Plugin Error"] = str(e)
        return dict(errors)  # get rid of defaultdict

    ##############################
    #
    # Supporting private methods:
    #
    ##############################

    # @refactor if removing local TSV validation
    def __get_ref_errors(self, ref_type: str, path: Path, assay_type: str) -> dict:
        if ref_type == "data":
            return get_data_dir_errors(
                assay_type, path, dataset_ignore_globs=self.dataset_ignore_globs
            )
        else:
            return get_tsv_errors(
                schema_name=ref_type,
                tsv_path=path,
                offline=self.offline,
                encoding=self.encoding,
                ignore_deprecation=self.ignore_deprecation,
            )

    # @delete if removing local TSV validation
    def __get_assay_tsv_errors(self, assay_type: str, path: Path) -> dict:
        return get_tsv_errors(
            schema_name=assay_type,
            tsv_path=path,
            offline=self.offline,
            encoding=self.encoding,
            optional_fields=self.optional_fields,
            ignore_deprecation=self.ignore_deprecation,
        )

    # @delete if removing local TSV validation; logic reflected in get_directory_errors for CEDAR
    def __get_assay_reference_errors(self, assay_type: str, path: Path) -> dict:
        try:
            rows = dict_reader_wrapper(path, self.encoding)
        except UnicodeDecodeError as e:
            return get_context_of_decode_error(e)
        except IsADirectoryError:
            return f"Expected a TSV, found a directory at {path}."
        if "data_path" not in rows[0] or "contributors_path" not in rows[0]:
            return "File is missing data_path or contributors_path."
        if not self.directory_path:
            return None

        errors = {}
        for i, row in enumerate(rows):
            row_number = f"row {i+2}"
            for ref in ["data", "contributors", "antibodies"]:
                field = f"{ref}_path"
                if not row.get(field):
                    continue
                path = self.directory_path / row[field]
                ref_errors = self.__get_ref_errors(ref, path, assay_type)
                if ref_errors:
                    errors[f"{row_number}, {ref} {path}"] = ref_errors

        return errors

    def __get_no_ref_errors(self) -> dict:
        if not self.directory_path:
            return {}
        referenced_data_paths = (
            set(self.__get_data_references().keys())
            | set(self.__get_contributors_references().keys())
            | set(self.__get_antibodies_references().keys())
        )
        non_metadata_paths = {
            path.name
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
