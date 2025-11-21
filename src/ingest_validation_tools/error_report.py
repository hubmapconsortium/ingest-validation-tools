from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field, fields
from datetime import datetime
from enum import Enum
from os.path import relpath
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Optional,
    Union,
)

from yaml import Dumper, dump

from ingest_validation_tools.local_validation.table_validator import ReportType

if TYPE_CHECKING:
    from ingest_validation_tools.upload import Upload

# Force dump not to use alias syntax.
# https://stackoverflow.com/questions/13518819/avoid-references-in-pyyaml
Dumper.ignore_aliases = lambda *_: True  # type: ignore

"""
How to prepare an error report:
    Within an upload:
        self.errors = ErrorManager(self)
        self.errors.append(Errors.ERROR_ENUM, "error value", path="/path", etc.)
        error_report = self.errors.report
"""


class Errors(Enum):
    PREFLIGHT = "Pre-Validation Errors"
    UPLOAD_METADATA = "Antibodies/Contributors Errors"
    METADATA_VALIDATION_LOCAL = "Local Validation Errors"
    METADATA_VALIDATION_API = "Spreadsheet Validator Errors"
    METADATA_URL_ERRORS = "URL Check Errors"
    METADATA_CONSTRAINT_ERRORS = "Entity Constraint Errors"
    DIRECTORY = "Directory Errors"
    REFERENCE = "Reference Errors"
    PLUGINS = "Data File Errors"
    PLUGINS_SKIPPED = "Data File checks skipped"


class ErrorSerializer:
    """
    ErrorSerializer subclasses are instantiated for each Errors enum value
    and handle errors of that type. The managers receive errors from the
    ErrorManager.
    """

    def __init__(
        self,
        name: Errors,
        dir_path: str,
        report_type: ReportType = ReportType.STR,
    ):
        self.name = name
        self.dir_path = dir_path
        self.report_type = report_type
        self.data = None
        self.raw = []

    def __len__(self):
        return len(self.raw)

    def __getitem__(self, key):
        if isinstance(self.data, dict):
            return self.data.get(key)
        elif isinstance(self.data, list):
            return self.data[key]

    def __bool__(self):
        return bool(self.raw)

    def __repr__(self):
        return f"ErrorList({self.data})"

    def as_dict(self) -> dict:
        if not self.data:
            return {}
        if isinstance(self.data, defaultdict):
            return {self.name.value: dict(self.data)}
        return {self.name.value: self.data}

    def add(self, error: Error):
        self.raw.append(error)

    def clean_error(self, error: Error) -> dict:
        cleaned_data = {}
        for err_field in fields(error):
            field_val = getattr(error, err_field.name)
            if err_field.name == "path" and field_val:
                cleaned_data["path"] = relpath(field_val, self.dir_path)
            elif err_field.name == "error":
                cleaned_data["error"] = error.by_report_type(self.report_type)
            elif err_field.name == "needs_formatting":
                continue
            else:
                cleaned_data[err_field.name] = field_val
            if note := error.notes.get(err_field.name):
                cleaned_data[err_field.name] = f"{cleaned_data[err_field.name]} ({note})"
        return cleaned_data

    def errors_only(self):
        if isinstance(self.data, defaultdict):
            return dict(self.data)
        return self.data

    def by_path(self, path: str | Path):
        errors = []
        for error in self.raw:
            if error.path == path:
                errors.append(error.by_report_type(self.report_type))
        return errors

    def counts(self) -> dict[str, int]:
        raise NotImplementedError


class ListErrorSerializer(ErrorSerializer):
    """
    default:
    Error Type:
        Path:
            - error

    Errors:PLUGINS:
    Data File Errors:
        <plugin description>:  # subtype
            - error

    """

    structure = {Errors.PLUGINS: "subtype"}

    def __init__(self, name, dir_path, report_type):
        super().__init__(name, dir_path, report_type)
        self.data = defaultdict(list)

    def add(self, error: Error):
        super().add(error)
        cleaned_error = self.clean_error(error)
        organizing_key = self.structure.get(self.name, "path")
        self.data[cleaned_error.get(organizing_key)].append(cleaned_error.get("error"))

    def counts(self):
        return {self.name.value: sum([len(val) for val in self.data.values()])}


class DictErrorSerializer(ErrorSerializer):
    """
    Errors.DIRECTORY:
    Directory Errors:
        ./path (as schema):  # path (note)
            Not allowed:  # subtype
                - error

    Errors.REFERENCE:
    Reference Errors:
        Shared directory references:  # subtype
            Subtype:  # ref_type
                - file  # error
        Multiple references:  # subtype
            Ref: # ref_type
                - location  # error
                - location  # error
        No references:  # subtype
            Files:  # ref_type
                - file  # error
                - file  # error
            Directories:  # ref_type
                - dir  # error
    """

    structure = {
        Errors.DIRECTORY: ["path", "subtype"],
        Errors.REFERENCE: ["subtype", "ref_type"],
    }

    def __init__(self, name, dir_path, report_type):
        super().__init__(name, dir_path, report_type)
        self.dict_data = defaultdict(lambda: defaultdict(list))
        self.list_data = defaultdict(list)

    def add(self, error: Error):
        super().add(error)
        cleaned_error = self.clean_error(error)
        primary_org_key = self.structure[self.name][0]
        secondary_org_key = self.structure[self.name][1]
        if secondary_org_val := cleaned_error.get(secondary_org_key):
            self.dict_data[cleaned_error.get(primary_org_key)].update(
                {secondary_org_val: cleaned_error["error"]}
            )
        else:
            self.list_data[cleaned_error.get(primary_org_key)].append(cleaned_error["error"])

    def as_dict(self) -> dict:
        if not self.dict_data and not self.list_data:
            return {}
        cleaned_data = {}
        for key, sub_dict in self.dict_data.items():
            cleaned_data[key] = dict(sub_dict)
        for key, sub_list in self.list_data.items():
            cleaned_data[key] = sub_list
        return {self.name.value: cleaned_data}

    def counts(self):
        counts = 0
        for sub_errors in self.dict_data.values():
            counts += len(sub_errors.keys())
        for sub_errors in self.list_data.values():
            counts += len(sub_errors)
        return {self.name.value: counts}


class StrErrorSerializer(ErrorSerializer):
    """
    Errors.PREFLIGHT:
    Pre-Validation Errors: error

    Errors.PLUGINS_SKIPPED:
    Data File checks skipped: Errors in metadata or directory structure.
    """

    def __init__(self, name, dir_path, report_type):
        super().__init__(name, dir_path, report_type)

    def add(self, error: Error):
        super().add(error)
        self.data = error.error

    def counts(self):
        return {self.name.value: 1 if self.data else 0}


@dataclass
class Error:
    error_type: Errors
    error: str | list | dict
    path: Optional[Union[str, Path]] = None
    subtype: Optional[str] = None
    notes: dict[str, str] = field(default_factory=dict)
    row: Optional[Union[str, int]] = None
    column: Optional[str] = None
    ref_type: str = ""
    needs_formatting: bool = False

    def __post_init__(self):
        if self.needs_formatting:
            self.format_validation_error()

    ##########
    # Format #
    ##########

    def by_report_type(self, report_type: ReportType = ReportType.STR):
        if report_type == ReportType.STR:
            return self.to_str()
        return self.to_json()

    def to_json(self):
        return {"column": self.column, "error": self.error, "row": self.row}

    def to_str(self) -> str:
        error_str = ""
        if self.row:
            error_str += f"On row(s) {self.row},"
        if self.column:
            error_str = (
                f'{error_str} column "{self.column}"'
                if error_str
                else f'In column "{self.column}"'
            )
        if error_str:
            return f"{error_str}: {str(self.error)}"
        return str(self.error)

    def format_validation_error(self):
        assert isinstance(self.error, dict)
        value = self.error.get("value")
        column = self.error.get("column")
        row = self.error.get("row")
        error_text = self.error.get("error_text")
        errorType = self.error.get("errorType")
        example = self.error.get("repairSuggestion")
        try:
            self.row = int(row) + 2  # type: ignore
        except ValueError:
            self.row = row
        self.column = column
        error = f'Value "{value}" fails because of error "{errorType}"'
        if error_text:
            error += f": {error_text}"
        if example:
            error += f". {example}"
        self.error = error


@dataclass
class InfoDict:
    time: Optional[datetime] = None
    git: Optional[str] = None
    dir: Optional[str] = None
    tsvs: dict[str, dict[str, Optional[str]]] = field(default_factory=dict)
    successful_plugins: list[str] = field(default_factory=list)

    def as_dict(self):
        as_dict = {
            "Time": self.time,
            "Git version": self.git,
            "Directory": self.dir,
            "TSVs": self.tsvs,
        }
        if self.successful_plugins:
            as_dict["Successful Plugins"] = self.successful_plugins
        return as_dict


class ErrorManager:
    """
    Errors are passed to ErrorManager by appending Error instances:
        errors = ErrorManager(upload)
        errors.append(
            Error(
                {"type": type_enum,
                 "path": path,
                 "notes": {"error_type": "as <schema>"},
                 "error_subtype": <e.g. Not allowed>,
                 "error": <list or str that's treated like a list on the backend>
                 }
            )
        )

    The ErrorManager then directs errors to the appropriate ErrorSerializer
    based on their error_type (Errors enum value). The serializers handle
    serializing their own data and preparing counts. The ErrorManager
    concatenates the errors / counts from its serializers in order to prepare
    the error report.
    """

    error_serializers = {
        Errors.PREFLIGHT: StrErrorSerializer,
        Errors.DIRECTORY: DictErrorSerializer,
        Errors.UPLOAD_METADATA: ListErrorSerializer,
        Errors.METADATA_VALIDATION_LOCAL: ListErrorSerializer,
        Errors.METADATA_VALIDATION_API: ListErrorSerializer,
        Errors.METADATA_URL_ERRORS: ListErrorSerializer,
        Errors.METADATA_CONSTRAINT_ERRORS: ListErrorSerializer,
        Errors.REFERENCE: DictErrorSerializer,
        Errors.PLUGINS: ListErrorSerializer,
        Errors.PLUGINS_SKIPPED: StrErrorSerializer,
    }

    def __init__(self, upload: Upload):
        self.upload = upload
        self.serializers = self._init_data_structures()
        self.serialized_errors = None
        self._data = []

    ##################
    # Public Methods #
    ##################

    def __bool__(self):
        return bool(self._data)

    @property
    def report(self) -> dict:
        if not self.serialized_errors:
            self.serialized_errors = self.create_report()
        return self.serialized_errors

    def append(self, error_type: Errors, error: str | list | dict, **kwargs):
        err = Error(error_type, error, **kwargs)
        self._data.append(err)
        error_dict = self.serializers[error_type]
        error_dict.add(err)

    def counts(self) -> dict:
        counts = {}
        for error_class in self.serializers.values():
            counts.update(error_class.counts())
        return counts

    def create_report(self) -> dict:
        serialized_data = {}
        for error_class in self.serializers.values():
            errors = error_class.as_dict()
            if errors:
                serialized_data.update(errors)
        return serialized_data

    def create_single_path_report(self, specified_path: str | Path) -> list:
        """
        Access directly to get errors for a specific path.
        """
        return self._get_by_path(specified_path)

    ######################
    # Supporting Methods #
    ######################

    def _init_data_structures(self) -> dict:
        data_structures = {}
        for error_type, structure_type in self.error_serializers.items():
            data_structures[error_type] = structure_type(
                error_type,
                dir_path=self.upload.directory_path,
                report_type=self.upload.report_type,
            )
        return data_structures

    def _get_by_path(self, path: str | Path) -> list:
        errors_by_path = []
        for error_class in self.serializers.values():
            errors_by_path.extend(error_class.by_path(path))
        return errors_by_path

    #####################
    # Report Formatting #
    #####################

    def _no_errors(self):
        return f"No errors!\n{dump(self.upload.info.as_dict(), sort_keys=False)}\n"

    def _as_list(self) -> list[str]:
        return _build_list(self.report)

    def as_text_list(self) -> str:
        return "\n".join(str(error) for error in self._as_list()) or self._no_errors()

    def as_yaml(self) -> str:
        return dump(self.report, sort_keys=False)

    def as_text(self) -> str:
        if not self.report:
            return self._no_errors()
        else:
            return self.as_yaml()

    def as_md(self) -> str:
        return f"```\n{self.as_text()}```"


def _build_list(anything, path=None) -> list[str]:
    """
    >>> flat = _build_list({
    ...     'nested dict': {
    ...         'like': 'this'
    ...     },
    ...     'nested array': [
    ...         'like',
    ...         'this'
    ...     ],
    ...     'string': 'like this',
    ...     'number': 42
    ... })
    >>> print('\\n'.join(flat))
    nested dict: like: this
    nested array: like
    nested array: this
    string: like this
    number: 42

    """
    prefix = f"{path}: " if path else ""
    if isinstance(anything, dict):
        if all(isinstance(v, (float, int, str)) for v in anything.values()):
            return [f"{prefix}{k}: {v}" for k, v in anything.items()]
        else:
            to_return = []
            for k, v in anything.items():
                to_return += _build_list(v, path=f"{prefix}{k}")
            return to_return
    elif isinstance(anything, list):
        if all(isinstance(v, (float, int, str)) for v in anything):
            return [f"{prefix}{v}" for v in anything]
        else:
            to_return = []
            for v in anything:
                to_return += _build_list(v, path=path)
            return to_return
    else:
        return [f"{prefix}{anything}"]
