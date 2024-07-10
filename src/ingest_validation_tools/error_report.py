from collections import defaultdict
from dataclasses import dataclass, field, fields
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import DefaultDict, Dict, List, Optional, Union

from yaml import Dumper, dump

from ingest_validation_tools.message_munger import munge, recursive_munge

# Force dump not to use alias syntax.
# https://stackoverflow.com/questions/13518819/avoid-references-in-pyyaml
Dumper.ignore_aliases = lambda *args: True


class ErrorDictException(Exception):
    def __init__(self, error: str):
        super().__init__(error)
        self.error = error


# Human readable error type strings.
class ErrorStrings(str, Enum):
    PREFLIGHT = "Preflight Errors"
    DIRECTORY = "Directory Errors"
    UPLOAD_METADATA = "Antibodies/Contributors Errors"
    METADATA_VALIDATION_LOCAL = "Local Validation Errors"
    METADATA_VALIDATION_API = "Spreadsheet Validator Errors"
    METADATA_URL_ERRORS = "URL Check Errors"
    METADATA_CONSTRAINT_ERRORS = "Entity Constraint Errors"
    REFERENCE = "Reference Errors"
    PLUGIN = "Data File Errors"
    PLUGIN_SKIP = "Fatal Errors"


# String versions of ErrorDict attribute names.
class ErrorAttrs(str, Enum):
    PREFLIGHT = "preflight"
    DIRECTORY = "directory"
    UPLOAD_METADATA = "upload_metadata"
    METADATA_VALIDATION_LOCAL = "metadata_validation_local"
    METADATA_VALIDATION_API = "metadata_validation_api"
    METADATA_CONSTRAINT_ERRORS = "metadata_constraint_errors"
    METADATA_URL_ERRORS = "metadata_url_errors"
    REFERENCE = "reference"
    PLUGIN = "plugin"
    PLUGIN_SKIP = "plugin_skip"


FIELD_MAP: Dict[ErrorAttrs, ErrorStrings] = {
    ErrorAttrs.PREFLIGHT: ErrorStrings.PREFLIGHT,
    ErrorAttrs.DIRECTORY: ErrorStrings.DIRECTORY,
    ErrorAttrs.UPLOAD_METADATA: ErrorStrings.UPLOAD_METADATA,
    ErrorAttrs.METADATA_VALIDATION_LOCAL: ErrorStrings.METADATA_VALIDATION_LOCAL,
    ErrorAttrs.METADATA_VALIDATION_API: ErrorStrings.METADATA_VALIDATION_API,
    ErrorAttrs.METADATA_URL_ERRORS: ErrorStrings.METADATA_URL_ERRORS,
    ErrorAttrs.METADATA_CONSTRAINT_ERRORS: ErrorStrings.METADATA_CONSTRAINT_ERRORS,
    ErrorAttrs.REFERENCE: ErrorStrings.REFERENCE,
    ErrorAttrs.PLUGIN: ErrorStrings.PLUGIN,
    ErrorAttrs.PLUGIN_SKIP: ErrorStrings.PLUGIN_SKIP,
}


@dataclass
class InfoDict:
    time: Optional[datetime] = None
    git: Optional[str] = None
    dir: Optional[str] = None
    tsvs: Dict[str, Dict[str, str]] = field(default_factory=dict)
    successful_plugins: list[str] = field(default_factory=list)

    def as_dict(self):
        as_dict = {
            "Time": self.time,
            "Git version": self.git,
            "Directory": self.dir,
            # "Directory schema version": self.dir_schema,
            "TSVs": self.tsvs,
        }
        if self.successful_plugins:
            as_dict["Successful Plugins"] = self.successful_plugins
        return as_dict


@dataclass
class ErrorDict:
    """
    Has fields for each major validation type, which can be accessed directly or
    compiled using self.as_dict().
    """

    preflight: Optional[str] = None
    directory: DefaultDict[str, List[str]] = field(default_factory=lambda: defaultdict(list))
    upload_metadata: DefaultDict[str, List[str]] = field(default_factory=lambda: defaultdict(list))
    metadata_validation_local: DefaultDict[str, List[str]] = field(
        default_factory=lambda: defaultdict(list)
    )
    metadata_validation_api: DefaultDict[str, List] = field(
        default_factory=lambda: defaultdict(list)
    )
    metadata_url_errors: DefaultDict[str, List] = field(default_factory=lambda: defaultdict(list))
    metadata_constraint_errors: DefaultDict[str, List] = field(
        default_factory=lambda: defaultdict(list)
    )
    reference: DefaultDict[str, Dict] = field(default_factory=lambda: defaultdict(dict))
    plugin: Dict[str, List[str]] = field(default_factory=dict)
    plugin_skip: Optional[str] = None

    def __bool__(self):
        """
        Return true if any field has errors.
        """
        return bool(self.as_dict())

    def errors_by_path(
        self, path: str, selected_fields: Optional[List[ErrorAttrs]] = None
    ) -> Dict:
        errors = {}
        if not selected_fields:
            selected_fields = [getattr(self, error_field.name) for error_field in fields(self)]
        for metadata_field in selected_fields:
            field_errors = getattr(self, metadata_field)
            if type(field_errors) is str:
                errors[FIELD_MAP[metadata_field]] = field_errors
            else:
                for key, value in field_errors.items():
                    if (Path(key) == Path(path)) or (path in key):
                        errors[FIELD_MAP[metadata_field]] = value
                        break
        return errors

    def online_only_errors_by_path(self, path: str):
        return self.errors_by_path(
            path,
            [
                ErrorAttrs.METADATA_URL_ERRORS,
                ErrorAttrs.METADATA_VALIDATION_API,
                ErrorAttrs.METADATA_CONSTRAINT_ERRORS,
            ],
        )

    def tsv_only_errors_by_path(self, path: str, local_allowed=True) -> List[str]:
        """
        For use in front-end single TSV validation.
        Turn off support for local validation by passing local_allowed=False
        """
        errors = []
        selected_fields = [
            ErrorAttrs.METADATA_URL_ERRORS,
            ErrorAttrs.METADATA_VALIDATION_API,
            ErrorAttrs.METADATA_CONSTRAINT_ERRORS,
        ]
        if local_allowed:
            selected_fields.append(ErrorAttrs.METADATA_VALIDATION_LOCAL)
        path_errors = self.errors_by_path(path, selected_fields)
        for value in path_errors.values():
            errors.extend(value)
        return errors

    def as_dict(self, attr_keys=False):
        """
        Compiles all fields with errors into a dict.
        By default uses human-readable keys, but passing
        attr_keys=True will use the attribute names matching the
        keys in FIELD_MAP.
        """
        errors = {}
        for error_field in fields(self):
            value = getattr(self, error_field.name)
            if value:
                value = self.sort_val(value)
                if attr_keys:
                    errors[error_field.name] = value
                else:
                    # TODO: clunky; should be able to refactor with addition of StrEnum in 3.11
                    error_enum = getattr(ErrorAttrs, error_field.name.upper())
                    error_name = FIELD_MAP.get(error_enum)
                    if error_name:
                        errors[error_name.value] = value
        return errors

    def sort_val(self, value):
        """
        Recursively sort all dicts by keys for consistency of testing and output.
        """
        if type(value) in [dict, defaultdict]:
            value = {k: self.sort_val(v) for k, v in sorted(value.items())}
        return value


class ErrorReport:
    def __init__(self, errors: Optional[ErrorDict] = None, info: Optional[InfoDict] = None):
        self.raw_errors = None
        self.raw_info = None
        self.errors = None
        self.info = None
        if errors:
            self.raw_errors = errors
            self.errors = errors.as_dict()
        if info:
            self.raw_info = info
            self.info = info.as_dict()

    @property
    def counts(self) -> Optional[dict[str, Union[int, str]]]:
        # Should this work with just errors dict?
        if not self.raw_errors:
            return {}
        counts = {}
        if self.raw_errors.preflight:
            return {ErrorStrings.PREFLIGHT: self.raw_errors.preflight}
        for error_type, errors in self.raw_errors.as_dict(attr_keys=True):
            if error_type in [ErrorAttrs.PREFLIGHT, ErrorAttrs.PLUGIN_SKIP, ErrorAttrs.PLUGIN]:
                continue
            errors = getattr(self.raw_errors, error_type)
            errors_for_category = 0
            if isinstance(errors, list):
                errors_for_category += len(errors)
            elif isinstance(errors, dict):
                errors_for_category += sum([len(nested_error) for nested_error in errors.values()])
            if errors_for_category:
                counts[FIELD_MAP[error_type]] = errors_for_category
        if self.raw_errors.plugin:
            plugin_counts = [len(value) for value in self.raw_errors.plugin.values()]
            plugin_error_str = f"{sum(plugin_counts)} errors in {len(plugin_counts)} plugins"
            counts[ErrorStrings.PLUGIN] = plugin_error_str
        if self.raw_errors.plugin_skip:
            counts[ErrorStrings.PLUGIN_SKIP] = True
        return counts

    def _no_errors(self):
        return f"No errors!\n{dump(self.info, sort_keys=False)}\n"

    def _as_list(self) -> List[Union[str, int]]:
        return [munge(m) for m in _build_list(self.errors)]

    def as_text_list(self) -> str:
        return "\n".join(str(error) for error in self._as_list()) or self._no_errors()

    def as_yaml(self) -> str:
        return dump(recursive_munge(self.errors), sort_keys=False)

    def as_text(self) -> str:
        if not self.errors:
            return self._no_errors()
        else:
            return self.as_yaml()

    def as_md(self) -> str:
        return f"```\n{self.as_text()}```"


def _build_list(anything, path=None) -> List[str]:
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
