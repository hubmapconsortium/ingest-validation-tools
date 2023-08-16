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
from ingest_validation_tools.schema_loader import PreflightError
from ingest_validation_tools.validation_utils import (
    dict_reader_wrapper,
    get_context_of_decode_error,
    get_data_dir_errors,
    get_directory_schema_versions,
    get_table_schema_version,
    get_tsv_errors,
)

TSV_SUFFIX = "metadata.tsv"
API_KEY_SECRET = "d72052d0b8c37b286cb8ddfab63e8fad4069766fc6229af33e675f799b76a6d4"


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

        try:
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

    def check_upload(self) -> dict:
        upload_errors = {}
        tsv_errors = self._get_local_tsv_errors()
        if tsv_errors:
            upload_errors["TSV Errors"] = tsv_errors
        dir_errors = self._get_directory_errors()
        if dir_errors:
            upload_errors["Directory Errors"] = dir_errors
        return upload_errors

    def validation_routine(self) -> dict:
        errors = {}
        local_validated = {}
        api_validated = {}
        for tsv_path, schema_version in self.effective_tsv_paths.items():
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
                local_errors = self.__get_assay_tsv_errors(
                    schema_version.schema_name, tsv_path
                )
                if local_errors:
                    local_validated[
                        f"{tsv_path} (as {schema_version.schema_name})"
                    ] = local_errors
            else:
                api_errors = self._api_validation(tsv_path)
                if api_errors:
                    api_validated[f"{tsv_path}"] = api_errors
        if local_validated:
            errors["Local Validation Errors"] = local_validated
        if api_validated:
            errors["CEDAR Validation Errors"] = api_validated
        return errors

    ###################################
    #
    # Top-level private methods:
    #
    ###################################

    def _get_local_tsv_errors(self) -> dict | None:
        errors = {}
        if not self.effective_tsv_paths:
            errors["Missing"] = "There are no effective TSVs."
            return errors
        else:
            types_counter = Counter(
                [v.schema_name for v in self.effective_tsv_paths.values()]
            )
            repeated = [
                assay_type for assay_type, count in types_counter.items() if count > 1
            ]
            if repeated:
                errors[
                    "Repeated"
                ] = f'There is more than one TSV for this type: {", ".join(repeated)}'
                raise ErrorDictException(errors)
        for path, schema_version in self.effective_tsv_paths.items():
            if not schema_version.is_assay:
                continue
            schema_name = schema_version.schema_name
            rows = self._get_rows_from_tsv(path)
            if type(rows) != list:
                errors[f"{path} (as {schema_name})"] = rows
            else:
                for ref in ["contributors", "antibodies"]:
                    for i, row in enumerate(rows):
                        # could break this find row value out
                        field = f"{ref}_path"
                        if not row.get(field):
                            continue
                        path = self.directory_path / row[field]
                        ref_error = self._check_path(
                            i, path, ref, schema_name, schema_version.version
                        )
                        if ref_error and errors.get(f"{path} (as {schema_name})"):
                            errors[f"{path} (as {schema_name})"].update(ref_error)
                        elif ref_error:
                            errors[f"{path} (as {schema_name})"] = ref_error
        return errors

    def _get_directory_errors(self) -> dict:
        errors = defaultdict()
        if not self.directory_path:
            return errors
        for path, schema_version in self.effective_tsv_paths.items():
            if not schema_version.is_assay:
                continue
            schema_name = schema_version.schema_name
            rows = self._get_rows_from_tsv(path)
            if type(rows) != list:
                errors[f"{path} (as {schema_name})"] = rows
            else:
                for i, row in enumerate(rows):
                    # could break this find row value out
                    if not row.get("data_path"):
                        continue
                    path = self.directory_path / row["data_path"]
                    dir_error = self._check_path(
                        i, path, "data", schema_name.lower(), schema_version.version
                    )
                    if dir_error and errors.get(f"{path} (as {schema_name})"):
                        errors[f"{path} (as {schema_name})"].update(dir_error)
                    elif dir_error:
                        errors[f"{path} (as {schema_name})"] = dir_error
        return errors

    def _cedar_api_call(self, tsv_path: str | Path) -> requests.Response:
        auth = HTTPBasicAuth(
            "apikey", API_KEY_SECRET if API_KEY_SECRET else os.environ[API_KEY_SECRET]
        )
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
        for metadata_path, schema_version in self.effective_tsv_paths.items():
            if not schema_version.is_assay:
                continue
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

    def _api_validation(self, tsv_path: Path):
        errors = {}
        response = self._cedar_api_call(tsv_path)
        if response.status_code != 200:
            errors["Request Errors"] = response.json()
        elif response.json()["reporting"] and len(response.json()["reporting"]) > 0:
            errors["Validation Errors"] = response.json()["reporting"]
        else:
            logging.info(f"No errors found during CEDAR validation for {tsv_path}!")
        return errors

    def _get_rows_from_tsv(self, path: str | Path) -> dict | list:
        errors = {}
        try:
            rows = dict_reader_wrapper(path, self.encoding)
            if "data_path" not in rows[0] or "contributors_path" not in rows[0]:
                errors[
                    "Path Errors"
                ] = "File is missing data_path or contributors_path."
            else:
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
    ) -> dict:
        errors = {}
        row_number = f"row {i+2}"
        if ref == "data":
            ref_errors = get_data_dir_errors(
                schema_name,
                path,
                schema_version,
                dataset_ignore_globs=self.dataset_ignore_globs,
            )
        else:
            ref_errors = get_tsv_errors(
                schema_name=ref,
                tsv_path=str(path),
                offline=self.offline,
                encoding=self.encoding,
                ignore_deprecation=self.ignore_deprecation,
            )
        if ref_errors:
            errors[f"{row_number}, {ref} {path}"] = ref_errors
        return errors

    def __get_assay_tsv_errors(self, assay_type: str, path: Path) -> dict:
        return get_tsv_errors(
            schema_name=assay_type,
            tsv_path=path,
            offline=self.offline,
            encoding=self.encoding,
            optional_fields=self.optional_fields,
            ignore_deprecation=self.ignore_deprecation,
        )

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
        for tsv_path, schema_version in self.effective_tsv_paths.items():
            if not schema_version.is_assay:
                continue
            for i, row in enumerate(dict_reader_wrapper(tsv_path, self.encoding)):
                if col_name in row:
                    reference = f"{tsv_path} (row {i+2})"
                    references[row[col_name]].append(reference)
        return references
