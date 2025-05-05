from __future__ import annotations

import json
import os
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, Literal, NamedTuple, Optional, Sequence, Union, overload

from yaml import dump

from ingest_validation_tools.table_validator import ReportType


# TODO: move to enums
class SerializeMode(Enum):
    CATEGORY = "collect_errors_by_category"
    FILE = "collect_errors_by_file"
    CATEGORY_THEN_FILE = "collect_errors_by_category_and_file"
    FILE_THEN_CATEGORY = "collect_errors_by_file_and_category"
    FLAT = "format_errors"  # just a list of formatted error strings or Error object dicts


class ErrorTypes(Enum):
    PREFLIGHT = "Preflight"
    DIRECTORY = "Directory Validation"
    UPLOAD_METADATA = "Antibodies/Contributors"
    METADATA_VALIDATION_API = "Spreadsheet Validator"
    METADATA_VALIDATION_LOCAL = "Local Validation"
    METADATA_VALIDATION_URLS = "URL Check"
    METADATA_VALIDATION_CONSTRAINTS = "Entity Constraint"
    REFERENCE = "Reference"
    PLUGIN = "Data File"


@dataclass
class Error:
    category: ErrorTypes
    errorContent: Union[str, dict, list]
    errorType: Optional[str] = None
    file: Optional[Union[str, Path]] = None
    schema: Optional[str] = None
    column: Optional[str] = None
    row: Optional[int] = None
    value: Optional[str] = None

    @overload
    def reformat(  # noqa: E704
        self, format_type: Union[None, Literal[ReportType.STR]] = ReportType.STR
    ) -> str: ...
    @overload
    def reformat(self, format_type: Literal[ReportType.JSON]) -> dict: ...  # noqa: E704
    def reformat(self, format_type: Optional[ReportType] = ReportType.STR):  # noqa: E301
        if format_type == ReportType.STR:
            return self.format_leaf_nodes_to_str()
        return self.format_to_json()

    def format_leaf_nodes_to_str(self, value: Optional[Union[dict, list]] = None):
        obj_to_format = value if value else self.errorContent
        if isinstance(obj_to_format, dict):
            formatted_dict = {}
            for key, value in obj_to_format.items():
                formatted_dict[key] = self.format_leaf_nodes_to_str(value)
            return formatted_dict
        elif isinstance(obj_to_format, list):
            formatted_list = []
            for value in obj_to_format:
                formatted_list.append(self.format_leaf_nodes_to_str(value))
            return formatted_list
        if self.row and self.column:
            return f"Row {self.row}, column '{self.column}': {obj_to_format}"
        else:
            return obj_to_format

    def format_to_json(self) -> dict:
        return asdict(self)


class ValidationReport:
    errors: list[Error] = []
    validation_completed: bool = False
    time: Optional[datetime] = None
    git: Optional[str] = None
    base_path: Optional[str] = None
    tsvs: Dict[str, Dict[str, str]] = field(default_factory=dict)
    successful_plugins: list[str] = field(default_factory=list)


class ValidationSerializer:

    def __init__(
        self,
        validation_report: ValidationReport,
        plugins_ran: bool = True,
        serialize_mode: Optional[SerializeMode] = None,
        format_type: ReportType = ReportType.STR,
        include_schema: bool = True,
        as_yaml: bool = False,
        detailed_success_report: bool = False,
    ):
        """
        Minimal instantiation:
            ValidationSerializer(validation_report)

        Can fine-tune output with the following params, set
        to defaults reflecting needs of HuBMAP ingest-pipeline:
            plugins_ran     whether plugins ran during validation
            serialize_mode  change organization of output
            format_type     errors as STR or JSON
            include_schema  format file path keys
                                True: "path (as schema 'schema')"
                                False: "path"
            as_yaml         default is to return JSON
            detailed_success_report
                            report info about validation run, default
                            is to return {} on successful validation
        """
        self.report = validation_report
        self.plugins_ran = plugins_ran
        self.serialize_mode = (
            serialize_mode if serialize_mode else SerializeMode.CATEGORY_THEN_FILE
        )
        self.format_type = format_type
        self.include_schema = include_schema
        self.as_yaml = as_yaml
        self.detailed_success_report = detailed_success_report

    ################
    # Custom types #
    ################

    class FileSchema(NamedTuple):
        filename: str
        schema: str

    FormattedErrorDict = dict[str, list[Union[str, dict]]]
    UnformattedErrorDict = dict[Union[str, ErrorTypes, FileSchema], list[Error]]

    ################
    # Main methods #
    ################

    def serialize(
        self,
    ) -> Union[str, dict]:
        if not self.report.validation_completed:
            raise Exception("Validation not complete, cannot serialize result.")
        # No errors, return validation report if requested.
        if not self.report.errors:
            if not self.detailed_success_report:
                return {}
            if self.as_yaml:
                return dump(self.validation_report())
            return self.validation_report()
        # Errors exist, serialize to either JSON or YAML
        serialize_func = getattr(
            self, "_" + self.serialize_mode.value, getattr(self, "format_errors")
        )
        if self.as_yaml:
            return dump(
                {self.report.base_path: self.format(serialize_func(self.report.errors))},
                sort_keys=False,
            )
        return json.dumps(
            {self.report.base_path: self.format(serialize_func(self.report.errors))},
            sort_keys=False,
        )

    def validation_report(self) -> dict:
        as_dict = {
            "Valid": bool(self.report.validation_completed and not self.report.errors),
            "Time": self.report.time,
            "Git version": self.report.git,
            "Base path": self.report.base_path,
            "TSVs": self.report.tsvs,
        }
        if self.report.successful_plugins:
            as_dict["Successful Plugins"] = self.report.successful_plugins
        return as_dict

    ####################
    # Reformat methods #
    ####################

    @overload
    def format(self, unformatted_errors: dict) -> FormattedErrorDict: ...  # noqa: E704
    @overload
    def format(self, unformatted_errors: list) -> list[Union[str, dict]]: ...  # noqa: E704
    def format(  # noqa: E301
        self,
        unformatted_errors: Union[dict, list],
    ) -> Union[FormattedErrorDict, Sequence[Union[str, dict]]]:
        formatted_errors = {}
        if isinstance(unformatted_errors, list):
            return self.format_errors(unformatted_errors)
        for key, value in unformatted_errors.items():
            key = self.format_key(key)
            if isinstance(value, dict):
                new_value = self.format(value)
            elif isinstance(value, list):
                new_value = self.format_errors(value)
            else:
                new_value = value
            formatted_errors[key] = new_value
        return formatted_errors

    def format_errors(self, errors: list[Error]) -> list[Union[str, dict]]:
        """
        Serialize Error objects to str or dict based on format_type.

        If self.format_type = ReportType.STR:
            [Error1, Error2, Error3] ->
            ["formatted_error1", "formatted_error2", "formatted_error3"]
        elif self.format_type = ReportType.JSON:
            [Error1, ...] ->
            [{"category": "error1Category", "errorText": "I am text for Error1", "file": "filename",
              "schema": None, "column": "column_name", "row": 1, "value": "value_str"}, ...]
        """
        formatted_errors = []
        for error in errors:
            if isinstance(error, str):
                formatted_errors.append(error)
            else:
                formatted_errors.append(error.reformat(self.format_type))
        return formatted_errors

    def format_key(self, key: Union[FileSchema, ErrorTypes, str]) -> str:
        """
        Category and file keys remain unformatted until the final step. Standardize to strings.
        """
        if isinstance(key, self.FileSchema):
            if self.include_schema:
                return f"{self.trunc_path(key[0])} (as schema '{key[1]}')"
            return self.trunc_path(key[0])
        elif isinstance(key, ErrorTypes):
            return key.value
        else:
            return key

    ####################
    # Structure errors #
    ####################

    def _collect_errors_by_category(self, error_list: list[Error]) -> UnformattedErrorDict:
        """
        Params:
            error_list: list[Error]
                        [Error1(category="Category1"), Error2(category="Category1"),
                        Error3(category="Category2"), Error4(category="Category2")]
        Return:
                {"Category1": [Error1, Error2], "Category2": [Error3, Error4]}
        """
        categorized_errors = defaultdict(list)
        for error in error_list:
            categorized_errors[error.category.value].append(error)
        return dict(categorized_errors)

    def _collect_errors_by_file(
        self, error_list: list[Error]
    ) -> list[Union[UnformattedErrorDict, str]]:
        """
        Params:
            error_list: list[Error]
                        [Error1(file="File1"), Error2(file="File1"),
                        Error3(file="File2"), Error4(file=None)]
        Return:
            {"File1": [Error1, Error2], "File2": [Error3], "Non-file errors": [Error4]}
        """
        errors = []
        errors_by_file = defaultdict(list)
        """
                File1:
                    Error1
                Error2
                Error3
            """
        for error in error_list:
            if file := error.file:
                errors_by_file[(file, error.schema)].append(error)
            else:
                errors.append(error)
        if errors_by_file:
            errors.append(dict(errors_by_file))
        return errors

    def _collect_errors_by_category_and_file(
        self, error_list: list[Error]
    ) -> dict[ErrorTypes, UnformattedErrorDict]:
        categorized_errors = self._collect_errors_by_category(error_list)
        categorized_errors_by_file = {}
        for category, errors in categorized_errors.items():
            categorized_errors_by_file[category] = self._collect_errors_by_file(errors)
        return categorized_errors_by_file

    def _single_file_validation_file_then_category(
        self, error_list: list[Error]
    ) -> dict[FileSchema, UnformattedErrorDict]:
        """
        For single-file validation only; discards any errors without a file attr.
        """
        errors_by_file = self._collect_errors_by_file(error_list)
        errors_by_file_and_category = {}
        for errors in errors_by_file:
            if isinstance(errors, dict):
                for key, value in errors.items():
                    errors_by_file_and_category[key] = self._collect_errors_by_category(value)
        return errors_by_file_and_category

    ##########
    # Counts #
    ##########

    def count_errors_by_category(self):
        counts = {}
        categorized_errors = self._collect_errors_by_category(self.report.errors)
        for category, errors in categorized_errors.items():
            if category == ErrorTypes.PLUGIN:
                if not self.plugins_ran and self.report.errors:
                    counts[category] = "Plugins skipped."
                    continue
            counts[category] = len(errors)
        return counts

    def count_errors_by_file(self):
        """
        Discards any errors without a file attr.
        """
        counts = {}
        errors_by_file = self._collect_errors_by_file(self.report.errors)
        for errors in errors_by_file:
            if isinstance(errors, dict):
                for filename, error_list in errors.items():
                    counts[filename] = len(error_list)
        return counts

    def trunc_path(self, path: Union[Path, str]):
        return os.path.relpath(path, self.report.base_path)

    # TODO: not sure if below is useful
    # ###########
    # # Filters #
    # ###########
    #
    # def filter_by_path(
    #     self,
    #     paths: list[str],
    #     categories: Optional[list[ErrorTypes]] = None,
    #     format: bool = True,
    # ) -> Union[UnformattedErrorDict, FormattedErrorDict]:
    #     errors_by_specified_paths = {}
    #     all_paths = self._collect_errors_by_file(self.report.errors)
    #     for path_val, value in all_paths.items():
    #         if isinstance(path_val, self.FileSchema) and path_val[0] in paths:
    #             errors_by_specified_paths[path_val] = (
    #                 value
    #                 if not categories
    #                 else self._errors_from_specified_categories(value, categories)
    #             )
    #     if not errors_by_specified_paths:
    #         return {}
    #     return errors_by_specified_paths if not format else self.format(errors_by_specified_paths)
    #
    # def filter_by_categories(
    #     self,
    #     categories: list[ErrorTypes],
    #     paths: Optional[list[str]] = None,
    #     format: bool = True,
    # ) -> Union[UnformattedErrorDict, FormattedErrorDict]:
    #     errors_by_specified_categories = {}
    #     all_categories = self._collect_errors_by_category(self.report.errors)
    #     for category, value in all_categories.items():
    #         if category in categories:
    #             errors_by_specified_categories[category] = (
    #                 value if not paths else self._errors_from_specified_paths(value, paths)
    #             )
    #     if not errors_by_specified_categories:
    #         return {}
    #     return (
    #         errors_by_specified_categories
    #         if not format
    #         else self.format(errors_by_specified_categories)
    #     )
    #
    # def _errors_from_specified_paths(
    #     self, errors: list[Error], paths: list[str]
    # ) -> UnformattedErrorDict:
    #     specified_paths = {}
    #     errors_by_path = self._collect_errors_by_file(errors)
    #     for fileschema, errors in errors_by_path.items():
    #         if isinstance(fileschema, self.FileSchema) and fileschema[0] in paths:
    #             specified_paths[fileschema] = errors
    #     return specified_paths
    #
    # def _errors_from_specified_categories(
    #     self, errors: list[Error], categories: list[ErrorTypes]
    # ) -> UnformattedErrorDict:
    #     specified_categories = {}
    #     categorized_errors = self._collect_errors_by_category(errors)
    #     for category, errors in categorized_errors.items():
    #         if category in categories:
    #             specified_categories[category] = errors
    #     return specified_categories
    #
    # def tsv_only_errors_by_path(self, paths: list[str]) -> FormattedErrorDict:
    #     tsv_error_types = [
    #         ErrorTypes.METADATA_VALIDATION_URLS,
    #         ErrorTypes.METADATA_VALIDATION_API,
    #         ErrorTypes.METADATA_VALIDATION_CONSTRAINTS,
    #         ErrorTypes.METADATA_VALIDATION_LOCAL,
    #     ]
    #     return self.format(self.filter_by_categories(tsv_error_types, paths))
    #


# TODO: testing
