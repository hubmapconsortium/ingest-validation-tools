from collections import defaultdict
from dataclasses import dataclass, field, fields
from datetime import datetime
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


@dataclass
class InfoDict:
    time: datetime
    git: str
    dir: str
    tsvs: Dict[str, Dict[str, str]]

    def as_dict(self):
        return {
            "Time": self.time,
            "Git version": self.git,
            "Directory": self.dir,
            # "Directory schema version": self.dir_schema,
            "TSVs": self.tsvs,
        }


@dataclass
class ErrorDict:
    """
    Has fields for each major validation type, which can be accessed directly or
    compiled using self.as_dict().
    """

    preflight: List[str] = field(default_factory=list)
    directory: DefaultDict[str, List[str]] = field(default_factory=lambda: defaultdict(list))
    upload_metadata: DefaultDict[str, List[str]] = field(default_factory=lambda: defaultdict(list))
    metadata_validation_local: DefaultDict[str, List[str]] = field(
        default_factory=lambda: defaultdict(list)
    )
    metadata_validation_api: DefaultDict[str, List] = field(
        default_factory=lambda: defaultdict(list)
    )
    metadata_url_errors: DefaultDict[str, List] = field(default_factory=lambda: defaultdict(list))
    reference: DefaultDict[str, Dict] = field(default_factory=lambda: defaultdict(dict))
    plugin: Dict[str, List[str]] = field(default_factory=dict)
    plugin_skip: Optional[str] = None

    def __bool__(self):
        """
        Return true if any field has errors.
        """
        return bool(self.as_dict())

    @property
    def field_map(self):
        """
        Single source of truth for top-level error dict key names.
        """
        return {
            "preflight": "Preflight Errors",
            "directory": "Directory Errors",
            "upload_metadata": "Antibodies/Contributors Errors",
            "metadata_validation_local": "Local Validation Errors",
            "metadata_validation_api": "Spreadsheet Validator Errors",
            "metadata_url_errors": "URL Check Errors",
            "reference": "Reference Errors",
            "plugin": "Data File Errors",
            "plugin_skip": "Fatal Errors",
        }

    def tsv_only_errors_by_path(self, path: str, local_allowed=False):
        """
        For use in front-end single TSV validation.
        """
        errors = {}
        for metadata_field in [
            "metadata_validation_local",
            "metadata_url_errors",
            "metadata_validation_api",
        ]:
            if metadata_field == "metadata_validation_local" and not local_allowed:
                continue
            for key, value in getattr(self, metadata_field).items():
                if Path(key) == Path(path):
                    errors[self.field_map.get(metadata_field)] = self.sort_val(value)
                    break
        return errors

    def as_dict(self):
        """
        Compiles all fields with errors into a dict.
        """
        errors = {}
        for error_field in fields(self):
            value = getattr(self, error_field.name)
            if value:
                value = self.sort_val(value)
                errors[self.field_map.get(error_field.name)] = value
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
