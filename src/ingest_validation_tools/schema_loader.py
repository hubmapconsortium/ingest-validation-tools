from __future__ import annotations

import re
from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set, Union

from ingest_validation_tools.enums import shared_enums
from ingest_validation_tools.yaml_include_loader import load_yaml

_table_schemas_path = Path(__file__).parent / "table-schemas"
_directory_schemas_path = Path(__file__).parent / "directory-schemas"
_pipeline_infos_path = Path(__file__).parent / "pipeline-infos/pipeline-infos.yaml"


def get_pipeline_infos(name: str) -> List[str]:
    infos = load_yaml(_pipeline_infos_path)
    return infos.get(name, [])


class PreflightError(Exception):
    def __init__(self, errors: Optional[str] = None):
        if errors:
            self.errors = errors


@dataclass
class SchemaVersion:
    """
    Create a SchemaVersion from soft assay types data.
    This assumes keys are predictable. If the rules tend to vary, we
    could add a class method like https://stackoverflow.com/q/72013377
    """

    # TODO: it would be great to be able to make more assumptions about
    # rows/assayclassifier data being present
    schema_name: str  # Valid values: canonical assay name OR other type
    version: str = ""
    directory_path: Optional[Path] = None
    table_schema: str = ""
    path: Optional[Union[Path, str]] = None
    rows: List = field(default_factory=list)
    soft_assay_data: Dict = field(default_factory=dict)
    is_cedar: bool = False
    dataset_type: str = ""  # String from assay_type or dataset_type field in TSV
    vitessce_hints: List = field(default_factory=list)
    dir_schema: str = ""
    metadata_type: str = "assays"
    contains: List = field(default_factory=list)

    def __post_init__(self):
        if type(self.path) is str:
            try:
                self.path = Path(self.path)
            except Exception as e:
                raise Exception(
                    f"""
                    SchemaVersion with name {self.schema_name} was passed
                    an invalid path: {self.path}. Error: {e}
                    """
                )
        if get_is_assay(self.schema_name):
            self.metadata_type = "assays"
        else:
            self.metadata_type = "others"
        if self.rows:
            self.get_row_data()
        if self.soft_assay_data:
            self.get_assayclassifier_data()
        if not self.version:
            if self.is_cedar:
                self.version = "2"
            else:
                self.version = "0"
        if not self.table_schema:
            self.table_schema = f"{self.schema_name}-v{self.version}"

    def get_row_data(self):
        if self.rows[0].get("metadata_schema_id"):
            self.is_cedar = True
        else:
            self.is_cedar = False
        self.version = self.rows[0].get("version")
        assay_type = self.rows[0].get("assay_type")
        dataset_type = self.rows[0].get("dataset_type")
        if assay_type is not None and dataset_type is not None:
            raise PreflightError(f"Found both assay_type and dataset_type for path {self.path}!")
        else:
            self.dataset_type = assay_type if assay_type else dataset_type

    def get_assayclassifier_data(self):
        self.vitessce_hints = self.soft_assay_data.get("vitessce-hints", [])
        self.dir_schema = self.soft_assay_data.get("dir-schema", "")
        self.table_schema = self.soft_assay_data.get("tbl-schema", "")
        match = re.match(r".+-v(\d+)", self.table_schema)
        if match:
            self.version = match[0]
        contains = self.soft_assay_data.get("must-contain", [])
        self.contains = [schema.lower() for schema in contains]


@dataclass
class DirSchemaVersion:
    dir_schema_name: str
    version: str
    dir_schema_string: str = ""
    assay_schema_name: str = ""
    filename: Union[str, Path] = ""
    path: Union[str, Path] = ""

    def __post_init__(self):
        self.dir_schema_string = self.dir_schema_name + "-v" + self.version


def get_fields_wo_headers(schema: dict) -> List[dict]:
    return [field for field in schema["fields"] if not isinstance(field, str)]


def get_field_enum(field_name: str, schema: dict) -> List[str]:
    fields_wo_headers = get_fields_wo_headers(schema)
    fields = [field for field in fields_wo_headers if field["name"] == field_name]
    if not fields:
        return []
    assert len(fields) == 1
    return fields[0]["constraints"]["enum"]


def list_table_schema_versions() -> List[SchemaVersion]:
    """
    >>> list_table_schema_versions()[0].table_schema
    '10x-multiome-v2'

    """
    schema_paths = list((_table_schemas_path / "assays").iterdir()) + list(
        (_table_schemas_path / "others").iterdir()
    )
    stems = sorted(p.stem for p in schema_paths if p.suffix == ".yaml")
    v_matches = [re.match(r"(.+)-v(\d+)", stem) for stem in stems]
    if not all(v_matches):
        raise Exception(f"All YAML should have version: {stems}")
    return [SchemaVersion(v_match[1], v_match[2]) for v_match in v_matches if v_match]


def dict_table_schema_versions() -> Dict[str, List[SchemaVersion]]:
    """
    >>> sorted([v.version for v in dict_table_schema_versions()['af']])
    ['0', '1', '2']
    """

    dict_of_lists = defaultdict(list)
    for sv in list_table_schema_versions():
        dict_of_lists[sv.schema_name].append(sv)
    return dict_of_lists


def list_directory_schema_versions() -> List[DirSchemaVersion]:
    """
    >>> list_directory_schema_versions()[0].dir_schema_string
    '10x-multiome-v2'
    """
    schema_paths = list(_directory_schemas_path.iterdir())
    stems = sorted(p.stem for p in schema_paths if p.suffix == ".yaml")
    parsed = [_parse_schema_version(stem) for stem in stems]
    return [DirSchemaVersion(sv[0], sv[1]) for sv in parsed]


def _parse_schema_version(stem: str) -> Sequence[str]:
    """
    >>> _parse_schema_version('abc-v0')
    ('abc', '0')
    >>> _parse_schema_version('xyz-v99-is the_best!')
    ('xyz', '99-is the_best!')
    """
    v_match = re.match(r"(.+)-v(\d+.*)", stem)
    if not v_match:
        raise Exception(f'No v match in "{stem}"')
    return v_match.groups()


# TODO: is this used anywhere?
def get_all_directory_schema_versions(schema_name: str) -> List[str]:
    return [
        schema_version.version
        for schema_version in list_directory_schema_versions()
        if schema_version.assay_schema_name == schema_name
    ]


def dict_directory_schema_versions() -> Dict[str, Set[str]]:
    dict_of_sets = defaultdict(set)
    for sv in list_directory_schema_versions():
        dict_of_sets[sv.dir_schema_name].add(sv.version)
    return dict_of_sets


def _get_schema_filename(schema_name: str, version: str) -> str:
    return f"{schema_name.lower()}-v{version}"


def get_table_schema(
    schema_version: SchemaVersion,
    optional_fields: List[str] = [],
    offline: bool = False,
    keep_headers: bool = False,
) -> dict:
    try:
        schema = load_yaml(
            Path(
                _table_schemas_path
                / schema_version.metadata_type
                / f"{schema_version.table_schema}.yaml"
            )
        )
    except FileNotFoundError:
        raise FileNotFoundError(
            f"No such file or directory: src/ingest_validation_tools/{schema_version.metadata_type}/{schema_version.table_schema}.yaml"  # noqa: E501
        )
    fields_wo_headers = get_fields_wo_headers(schema)
    if not keep_headers:
        schema["fields"] = fields_wo_headers

    names = [field["name"] for field in fields_wo_headers]
    for schema_field in schema["fields"]:
        if isinstance(schema_field, str):
            continue
        if schema_version.metadata_type == "assays":
            _add_level_1_description(schema_field)
            _validate_level_1_enum(schema_field)
        _add_constraints(schema_field, optional_fields, offline=offline, names=names)
        if schema_version.metadata_type == "assays":
            _validate_field(schema_field)

    return schema


def get_is_assay(schema_name: str) -> bool:
    # TODO: read from file system... but larger refactor may make it redundant.
    return schema_name not in [
        "donor",
        "organ",
        "sample",
        "antibodies",
        "contributors",
        "sample-block",
        "sample-section",
        "sample-suspension",
    ]


def get_directory_schema(
    dir_schema: Optional[str] = None,
    directory_type: Optional[str] = None,
    version_number: Optional[str] = None,
) -> Optional[Dict]:
    if not dir_schema and (directory_type and version_number):
        dir_schema = _get_schema_filename(directory_type, version_number)
    if not dir_schema:
        raise Exception("Not enough information to retrieve directory schema.")
    directory_schema_path = _directory_schemas_path / f"{dir_schema}.yaml"
    if not directory_schema_path.exists():
        return None
    schema = load_yaml(directory_schema_path)
    schema["files"] += []
    return schema


def _validate_field(field: dict) -> None:
    if field["name"].endswith("_unit") and "enum" not in field["constraints"]:
        raise Exception('"_unit" fields must have enum constraints', field)


def _add_level_1_description(field: dict) -> None:
    if "description" in field:
        return
    descriptions = {
        "assay_category": "Each assay is placed into one of the following 4 general categories: "
        "generation of images of microscopic entities, identification & quantitation of molecules "
        "by mass spectrometry, imaging mass spectrometry, and determination of nucleotide "
        "sequence.",
        "assay_type": "The specific type of assay being executed.",
        "analyte_class": "Analytes are the target molecules being measured with the assay.",
    }
    name = field["name"]
    if name in descriptions:
        field["description"] = descriptions[name]


def _validate_level_1_enum(field: dict) -> None:
    """
    >>> field = {'name': 'assay_category'}
    >>> _validate_level_1_enum(field)
    Traceback (most recent call last):
    ...
    KeyError: 'constraints'

    >>> field['constraints'] = {}
    >>> _validate_level_1_enum(field)
    Traceback (most recent call last):
    ...
    TypeError: 'NoneType' object is not iterable

    >>> field['constraints']['required'] = False
    >>> _validate_level_1_enum(field)

    (No error if not required!)

    >>> del field['constraints']['required']

    >>> field['constraints']['enum'] = ['fake']
    >>> try:
    ...     _validate_level_1_enum(field)
    ... except AssertionError as e:
    ...     print(',\\n'.join(str(e).split(',')))
    Unexpected enums for assay_category: {'fake'}
    Allowed: ['clinical_imaging',
     'derived_datasets',
     'fish',
     'histology',
     'imaging',
     'mass_spectrometry',
     'mass_spectrometry_imaging',
     'mxfbe',
     'organ',
     'sample',
     'sequence',
     'single_cycle_fluorescence_microscopy',
     'spatial_transcriptomics']
    """

    name = field["name"]
    if name in shared_enums:
        optional = not field["constraints"].get("required", True)  # Default: required = True
        actual = set(
            field["constraints"].get(
                "enum",
                [] if optional else None,
                # Only optional fields are allowed to skip the enum.
            )
        )
        allowed = set(shared_enums[name])
        assert actual <= allowed, (
            f"Unexpected enums for {name}: {actual - allowed}\n" f"Allowed: {sorted(allowed)}"
        )


def _add_constraints(
    field: dict, optional_fields: List[str], offline=None, names: List[str] = []
) -> None:
    """
    Modifies field in-place, adding implicit constraints
    based on the field name.

    Names (like "percent") are taken as hint about the data:

    >>> from pprint import pprint
    >>> field = {'name': 'abc_percent'}
    >>> _add_constraints(field, [])
    >>> pprint(field, width=40)
    {'constraints': {'maximum': 100,
                     'minimum': 0,
                     'required': True},
     'custom_constraints': {'forbid_na': True,
                            'sequence_limit': 3},
     'name': 'abc_percent',
     'type': 'number'}

    Fields can be made optional at run-time:

    >>> field = {'name': 'optional_value'}
    >>> _add_constraints(field, ['optional_value'])
    >>> pprint(field, width=40)
    {'constraints': {'required': False},
     'custom_constraints': {'forbid_na': True,
                            'sequence_limit': 3},
     'name': 'optional_value',
     'type': 'number'}

    Default field type is string:

    >>> field = {'name': 'whatever', 'constraints': {'pattern': 'fake-regex'}}
    >>> _add_constraints(field, [])
    >>> pprint(field, width=40)
    {'constraints': {'pattern': 'fake-regex',
                     'required': True},
     'custom_constraints': {'forbid_na': True,
                            'sequence_limit': 3},
     'name': 'whatever',
     'type': 'string'}

    Some fields are expected to have sequential numbers:

    >>> field = {'name': 'seq_expected', 'custom_constraints': {'sequence_limit': False}}
    >>> _add_constraints(field, [])
    >>> pprint(field, width=40)
    {'constraints': {'required': True},
     'custom_constraints': {'forbid_na': True},
     'name': 'seq_expected'}

    """
    if "constraints" not in field:
        field["constraints"] = {}
    if "custom_constraints" not in field:
        field["custom_constraints"] = {}

    # Guess constraints:
    if "required" not in field["constraints"]:
        field["constraints"]["required"] = True
    if "protocols_io_doi" in field["name"]:
        field["constraints"]["pattern"] = r"10\.17504/.*"
        field["custom_constraints"]["url"] = {"prefix": "https://dx.doi.org/"}
    if field["name"].endswith("_email"):
        field["format"] = "email"
        field["type"] = "string"

    # In the src schemas, set to False to avoid limit on sequences...
    if field["custom_constraints"].get("sequence_limit", True):
        field["custom_constraints"]["sequence_limit"] = 3
    else:
        del field["custom_constraints"]["sequence_limit"]
    # ... or to allow "N/A":
    if field["custom_constraints"].get("forbid_na", True):
        field["custom_constraints"]["forbid_na"] = True
    else:
        del field["custom_constraints"]["forbid_na"]

    if field["name"].endswith("_unit"):
        # Issues have been filed to make names more consistent:
        # https://github.com/hubmapconsortium/ingest-validation-tools/issues/645
        # https://github.com/hubmapconsortium/ingest-validation-tools/issues/646
        target = None
        for suffix in ["_value", ""]:
            target = field["name"].replace("_unit", suffix)
            if target in names:
                break
        if target in names:
            field["custom_constraints"]["units_for"] = target
            field["constraints"]["required"] = False

    # Guess types:
    if field["name"].startswith("is_"):
        field["type"] = "boolean"
    if field["name"].endswith("_value"):
        field["type"] = "number"
    if field["name"].startswith("number_of_"):
        field["type"] = "integer"
    if "percent" in field["name"]:
        field["type"] = "number"
        field["constraints"]["minimum"] = 0
        field["constraints"]["maximum"] = 100
    if "pattern" in field["constraints"]:
        field["type"] = "string"

    # Override:
    if field["name"] in optional_fields:
        field["constraints"]["required"] = False

    # Remove network checks if offline:
    if offline:
        c_c = "custom_constraints"
        if c_c in field and "url" in field[c_c]:
            del field[c_c]["url"]


def enum_maps_to_lists(schema, add_none_of_the_above=False, add_suggested=False):
    """
    >>> schema = {
    ...     'whatever': 'is preserved',
    ...     'fields': [
    ...         {'name': 'ice_cream',
    ...          'constraints': {
    ...                 'enum': {
    ...                     'vanilla': 'http://example.com/vanil',
    ...                     'chocolate': 'http://example.com/choco'}}},
    ...         {'name': 'mood',
    ...          'constraints': {
    ...                 'enum': ['happy', 'sad']}},
    ...         {'name': 'no_enum', 'constraints': {}},
    ...         {'name': 'no_constraints'},
    ...     ]}
    >>> from pprint import pprint
    >>> pprint(enum_maps_to_lists(schema))
    {'fields': [{'constraints': {'enum': ['vanilla', 'chocolate']},
                 'name': 'ice_cream'},
                {'constraints': {'enum': ['happy', 'sad']}, 'name': 'mood'},
                {'constraints': {}, 'name': 'no_enum'},
                {'name': 'no_constraints'}],
     'whatever': 'is preserved'}

    >>> pprint(enum_maps_to_lists(schema, add_none_of_the_above=True))
    {'fields': [{'constraints': {'enum': ['vanilla',
                                          'chocolate',
                                          'Submitter Suggestion']},
                 'name': 'ice_cream'},
                {'constraints': {'enum': ['happy', 'sad']}, 'name': 'mood'},
                {'constraints': {}, 'name': 'no_enum'},
                {'name': 'no_constraints'}],
     'whatever': 'is preserved'}

    >>> pprint(enum_maps_to_lists(schema, add_none_of_the_above=True, add_suggested=True))
    {'fields': [{'constraints': {'enum': ['vanilla',
                                          'chocolate',
                                          'Submitter Suggestion']},
                 'name': 'ice_cream'},
                {'description': 'Desired value for ice_cream',
                 'name': 'ice_cream_suggested'},
                {'constraints': {'enum': ['happy', 'sad']}, 'name': 'mood'},
                {'constraints': {}, 'name': 'no_enum'},
                {'name': 'no_constraints'}],
     'whatever': 'is preserved'}
    """
    schema_copy = deepcopy(schema)
    schema_copy["fields"], original_fields = [], schema_copy["fields"]
    for original_field in original_fields:
        extra_field = None
        if "constraints" in original_field:
            constraints = original_field["constraints"]
            if "enum" in constraints:
                if isinstance(constraints["enum"], dict):
                    constraints["enum"] = list(constraints["enum"].keys())
                    if add_none_of_the_above:
                        constraints["enum"].append("Submitter Suggestion")
                    if add_suggested:
                        extra_field = {
                            "name": f"{original_field['name']}_suggested",
                            "description": f"Desired value for {original_field['name']}",
                        }
        schema_copy["fields"].append(original_field)
        if extra_field:
            schema_copy["fields"].append(extra_field)
    return schema_copy
