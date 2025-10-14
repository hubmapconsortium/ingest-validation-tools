from __future__ import annotations

import re
from collections import defaultdict
from collections.abc import MutableMapping
from dataclasses import dataclass, field, fields
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, DefaultDict, Dict, List, Optional, Type, Union

from yaml import Dumper, dump

from ingest_validation_tools.local_validation.table_validator import ReportType

if TYPE_CHECKING:
    from ingest_validation_tools.upload import Upload

# Force dump not to use alias syntax.
# https://stackoverflow.com/questions/13518819/avoid-references-in-pyyaml
Dumper.ignore_aliases = lambda *args: True


@dataclass
class DictErrorType(MutableMapping):
    """
    Dataclass that acts like a defaultdict using self.value.
    """

    name: str = ""
    display_name: str = ""
    default_factory: Type = list
    value: DefaultDict = field(default_factory=lambda: defaultdict())
    allow_aesthetic_cleanup: bool = True

    def __post_init__(self):
        if type(self.default_factory) is not list:
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

    def __bool__(self):
        return bool(self.value)

    @property
    def counts(self) -> dict:
        if self.default_factory == list:
            return self.list_type_counts()
        elif self.default_factory == dict:
            return self.dict_type_counts()
        else:
            print(f"Counts method for defaultdict({self.default_factory}) not defined.")
            return {}

    def list_type_counts(self):
        errors_for_category = 0
        for errors in self.value.values():
            if type(errors) is list:
                errors_for_category += len(errors)
            elif type(errors) is dict:
                errors_for_category += len(errors.keys())
            else:
                errors_for_category += 1
        return {self.display_name: errors_for_category} if errors_for_category else {}

    def dict_type_counts(self):
        counts_by_sub_category = {}
        for error_type, errors in self.value.items():
            for error_sub_type, error in errors.items():
                if type(error) is list:
                    value = len(error)
                    counts_by_sub_category[error_type] = value
                else:
                    print(
                        f"Counting for {error_type} error '{error_sub_type}' of type {type(error)} not defined."
                    )
        return counts_by_sub_category

    @property
    def cleaned_value(self):
        return self.recursive_cleanup(self.value)

    def recursive_cleanup(self, message_collection):
        """
        Adapted from message_munger > recursive_munge,
        but much less concerned with verbiage.
        """
        if isinstance(message_collection, dict):
            return {str(k): self.recursive_cleanup(v) for k, v in message_collection.items()}
        elif isinstance(message_collection, list):
            return [self.recursive_cleanup(v) for v in message_collection]
        else:
            msg = str(message_collection)
            if self.allow_aesthetic_cleanup:
                return self.cleanup_terminal_nodes(msg)
            return msg

    def cleanup_terminal_nodes(self, message):
        if message is None:
            ret_message = ""
        elif isinstance(message, str):
            ret_message = message.replace("'", '"')
            ending_url_regex = r"\s((http|https).+)$"
            if re.search(ending_url_regex, ret_message):
                ret_message += " "
            elif not ret_message.endswith("."):
                ret_message += "."
        else:
            ret_message = str(message)
        return ret_message


@dataclass
class StrErrorType:
    name: str = ""
    display_name: str = ""
    value: Optional[str] = None
    allow_cleanup: bool = True

    def __bool__(self):
        return bool(self.value)

    @property
    def counts(self) -> dict:
        if self.allow_cleanup:
            value = self.cleaned_value
        else:
            value = self.value
        return {self.display_name: value} if value else {}

    @property
    def cleaned_value(self):
        if self.allow_cleanup and self.value:
            ret_message = self.value
            if not self.value.endswith("."):
                ret_message = self.value + "."
            return ret_message.replace("'", '"')
        return self.value


ErrorType = Union[StrErrorType, DictErrorType]


@dataclass
class InfoDict:
    time: Optional[datetime] = None
    git: Optional[str] = None
    dir: Optional[str] = None
    tsvs: Dict[str, Dict[str, Optional[str]]] = field(default_factory=dict)
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
        default_factory=lambda: DictErrorType(
            name="directory",
            display_name="Directory Errors",
            allow_aesthetic_cleanup=False,
        )
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
            name="reference",
            display_name="Reference Errors",
            default_factory=dict,
            allow_aesthetic_cleanup=False,
        )
    )
    plugin: DictErrorType = field(
        default_factory=lambda: DictErrorType(name="plugin", display_name="Data File Errors")
    )
    plugin_skip: StrErrorType = field(
        default_factory=lambda: StrErrorType(name="plugin_skip", display_name="Fatal Errors")
    )

    def __iter__(self):
        for attr_field in fields(self):
            yield getattr(self, attr_field.name)

    def __bool__(self):
        """
        Return true if any field has errors.
        """
        return bool(self.as_dict())

    def errors_by_path(
        self, path: str, selected_fields: list = [], report_type: ReportType = ReportType.STR
    ) -> Dict[str, str]:
        errors = {}
        if not selected_fields:
            selected_fields = [error_field for error_field in fields(self)]
        selected_error_type_fields = [field for field in selected_fields]
        for error_type_field in selected_error_type_fields:
            error_field = getattr(self, error_type_field.name, None)
            if not error_field or not error_field.value:
                continue
            if error_field.name == "preflight":
                if report_type == ReportType.JSON:
                    error_values = [{"error": error_field.cleaned_value}]
                else:
                    error_values = [error_field.cleaned_value]
            else:
                error_values = (
                    error_field.cleaned_value if report_type == ReportType.STR else error_field
                )
            if type(error_field) is StrErrorType:
                errors[error_field.display_name] = error_values
            elif type(error_field) is DictErrorType:
                for key, value in error_values.items():  # type: ignore
                    if (Path(path).resolve() == Path(key).resolve()) or (str(path) in str(key)):
                        errors[error_field.display_name] = value
                        break
        return errors

    def tsv_only_errors_by_path(
        self, path: str, report_type: ReportType = ReportType.STR, local_allowed=True
    ) -> List[str]:
        """
        For use in front-end single TSV validation.
        Turn off support for local validation by passing local_allowed=False
        """
        errors = []
        selected_fields = [
            self.preflight,
            self.metadata_url_errors,
            self.metadata_validation_api,
            self.metadata_constraint_errors,
        ]
        if local_allowed:
            selected_fields.append(self.metadata_validation_local)
        path_errors = self.errors_by_path(path, selected_fields, report_type)
        for value in path_errors.values():
            errors.extend(value)
        return errors

    def as_dict(self, attr_keys=False, report_type: ReportType = ReportType.STR):
        """
        Compiles all fields with errors into a dict.
        By default uses human-readable keys, but passing
        attr_keys=True will use the attribute names.
        """
        errors = {}
        for errordict_field in fields(self):
            error_field = getattr(self, errordict_field.name)
            if not error_field or not error_field.value:
                continue
            value = self.sort_val(
                error_field.cleaned_value if report_type == ReportType.STR else error_field
            )
            if attr_keys:
                errors[error_field.name] = value
            else:
                errors[error_field.display_name] = value
        return errors

    def sort_val(self, value):
        """
        Recursively stringify keys and sort all dicts by keys for consistency of testing and output.
        """
        if type(value) in [dict, defaultdict]:
            sorted_str_dict = dict(sorted({str(k): v for k, v in value.items()}.items()))
            value = {k: self.sort_val(v) for k, v in sorted_str_dict.items()}
        return value


class ErrorReport:
    errors = {}
    info = {}
    raw_errors = ErrorDict()
    raw_info = InfoDict()

    def __init__(
        self,
        upload: Optional[Upload] = None,
        errors: Optional[ErrorDict] = None,
        info: Optional[InfoDict] = None,
    ):
        if upload:
            self.upload = upload
            if not upload.get_errors_called:
                self.raw_errors = upload.get_errors()
            else:
                self.raw_errors = upload.errors
            if not upload.get_info_called:
                self.raw_info = upload.get_info()
            else:
                self.raw_info = upload.info
            self.errors = upload.errors.as_dict(report_type=upload.report_type)
            self.info = upload.info.as_dict()
        # Preserved for backward compatibility for now
        else:
            if errors:
                self.raw_errors = errors
                self.errors = errors.as_dict()
            if info:
                self.raw_info = info
                self.info = info.as_dict()

    @property
    def counts(self) -> Dict[str, Union[int, str]]:
        """
        Count errors per category. Requires raw_errors (ErrorDict object).
        ErrorType fields have a `counts` property, but fields related to
        plugins need some pre-processing.
        """
        if not self.raw_errors:
            return {}
        counts = {}
        for raw_error_field in fields(self.raw_errors):
            error_field = getattr(self.raw_errors, raw_error_field.name)
            if not error_field or not error_field.value:
                continue
            if error_field.name == "plugin":
                plugin_counts = [len(value) for value in self.raw_errors.plugin.values()]
                counts[self.raw_errors.plugin.display_name] = (
                    f"{sum(plugin_counts)} errors in {len(plugin_counts)} plugins"
                )
            elif error_field.name == "plugin_skip":
                counts["Plugins Skipped"] = True
            elif getattr(error_field, "counts"):
                counts.update(error_field.counts)
        return counts

    def _no_errors(self):
        return f"No errors!\n{dump(self.info, sort_keys=False)}\n"

    def _as_list(self) -> List[str]:
        return _build_list(self.errors)

    def as_text_list(self) -> str:
        return "\n".join(str(error) for error in self._as_list()) or self._no_errors()

    def as_yaml(self) -> str:
        return dump(self.errors, sort_keys=False)

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
