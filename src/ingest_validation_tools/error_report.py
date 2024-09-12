from collections import defaultdict
from collections.abc import MutableMapping
from dataclasses import dataclass, field, fields
from datetime import datetime
from pathlib import Path
from typing import DefaultDict, Dict, List, Optional, Sequence, Type, Union

from yaml import Dumper, dump

from ingest_validation_tools.message_munger import munge, recursive_munge

# Force dump not to use alias syntax.
# https://stackoverflow.com/questions/13518819/avoid-references-in-pyyaml
Dumper.ignore_aliases = lambda *args: True


class ErrorDictException(Exception):
    def __init__(self, error: str):
        super().__init__(error)
        self.error = error


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
class DictErrorType(MutableMapping):
    name: str = ""
    display_name: str = ""
    path: Optional[str] = None
    default_factory: Type = list
    value: DefaultDict = field(default_factory=lambda: defaultdict())

    def __post_init__(self):
        self.value = defaultdict(self.default_factory)

    def __missing__(self, key):
        self.value[key] = self.default_factory()
        return self.value[key]

    def __getitem__(self, key):
        return self.value[key]

    def __setitem__(self, key, value):
        self.value[key] = value

    def __delitem__(self, key):
        del self.value[key]

    def __iter__(self):
        return iter(self.value)

    def __len__(self):
        return len(self.value)


@dataclass
class StrErrorType:
    name: str = ""
    display_name: str = ""
    path: Optional[str] = None
    value: Optional[str] = None


ErrorType = Union[StrErrorType, DictErrorType]


@dataclass
class ErrorDict:
    """
    Has fields for each major validation type, which can be accessed directly or
    compiled using self.as_dict().
    """

    preflight: StrErrorType = field(
        default_factory=lambda: StrErrorType(name="preflight", display_name="Preflight Errors")
    )
    directory: DictErrorType = field(
        default_factory=lambda: DictErrorType(name="directory", display_name="Directory Errors")
    )
    upload_metadata: DictErrorType = field(
        default_factory=lambda: DictErrorType(
            name="upload_metadata", display_name="Antibodies/Contributors Errors"
        )
    )
    metadata_validation_local: DictErrorType = field(
        default_factory=lambda: DictErrorType(
            name="metadata_validation_local", display_name="Local Validation Errors"
        )
    )
    metadata_validation_api: DictErrorType = field(
        default_factory=lambda: DictErrorType(
            name="metadata_validation_api", display_name="Spreadsheet Validator Errors"
        )
    )
    metadata_url_errors: DictErrorType = field(
        default_factory=lambda: DictErrorType(
            name="metadata_url_errors", display_name="URL Check Errors"
        )
    )
    metadata_constraint_errors: DictErrorType = field(
        default_factory=lambda: DictErrorType(
            name="metadata_constraint_errors", display_name="Entity Constraint Errors"
        )
    )
    reference: DictErrorType = field(
        default_factory=lambda: DictErrorType(
            name="reference", display_name="Reference Errors", default_factory=dict
        )
    )
    plugin: DictErrorType = field(
        default_factory=lambda: DictErrorType(name="plugin", display_name="Data File Errors")
    )
    plugin_skip: StrErrorType = field(
        default_factory=lambda: StrErrorType(name="plugin_skip", display_name="Fatal Errors")
    )

    def __bool__(self):
        """
        Return true if any field has errors.
        """
        return bool(self.as_dict())

    def errors_by_path(self, path: str, selected_fields: list = []) -> Dict[str, str]:
        errors = {}
        if not selected_fields:
            selected_fields = [error_field for error_field in fields(self)]
        selected_error_type_fields = [
            field
            for field in selected_fields
            if field.type.__name__ in ["StrErrorType", "DictErrorType"]
        ]
        for field in selected_error_type_fields:
            error_field = getattr(self, field.name)
            if not error_field.value:
                continue
            if type(error_field) is StrErrorType:
                errors[error_field.display_name] = error_field.value
            elif type(error_field) is DictErrorType:
                for key, value in error_field.items():
                    if (Path(key) == Path(path)) or (str(path) in key):
                        errors[error_field.display_name] = value
                        break
        return errors

    def online_only_errors_by_path(self, path: str):
        return self.errors_by_path(
            path,
            [
                self.metadata_url_errors,
                self.metadata_validation_api,
                self.metadata_constraint_errors,
            ],
        )

    def tsv_only_errors_by_path(self, path: str, local_allowed=True) -> List[str]:
        """
        For use in front-end single TSV validation.
        Turn off support for local validation by passing local_allowed=False
        """
        errors = []
        selected_fields = [
            self.metadata_url_errors,
            self.metadata_validation_api,
            self.metadata_constraint_errors,
        ]
        if local_allowed:
            selected_fields.append(self.metadata_validation_local)
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
        for field in fields(self):
            error_field = getattr(self, field.name)
            if not error_field.value:
                continue
            value = self.sort_val(error_field.value)
            if attr_keys:
                errors[error_field.name] = value
            else:
                errors[error_field.display_name] = value
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
    def counts(self) -> Dict[str, Union[int, str]]:
        breakpoint()
        if not self.raw_errors:
            return {}
        counts = {}
        for field in fields(self.raw_errors):
            error_field = getattr(self.raw_errors, field.name)
            if isinstance(error_field, StrErrorType) or error_field.name == "plugin":
                continue
            elif isinstance(error_field, DictErrorType):
                errors_for_category = 0
                for errors in error_field.values():
                    if isinstance(errors, list):
                        errors_for_category += len(errors)
                    elif isinstance(errors, dict):
                        errors_for_category += sum(
                            [len(nested_error) for nested_error in errors.values()]
                        )
                if errors_for_category:
                    counts[error_field.display_name] = errors_for_category
        if self.raw_errors.plugin:
            plugin_counts = [len(value) for value in self.raw_errors.plugin.values()]
            plugin_error_str = f"{sum(plugin_counts)} errors in {len(plugin_counts)} plugins"
            counts[self.raw_errors.plugin.display_name] = plugin_error_str
        if self.raw_errors.plugin_skip:
            counts["Plugins Skipped"] = True
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
