from __future__ import annotations

import re
from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set, Union

from ingest_validation_tools.enums import (
    UNIQUE_FIELDS_MAP,
    DatasetType,
    EntityTypes,
    OtherTypes,
    Sample,
    shared_enums,
)
from ingest_validation_tools.yaml_include_loader import load_yaml

_table_schemas_path = Path(__file__).parent / "table-schemas"
_directory_schemas_path = Path(__file__).parent / "directory-schemas"
_pipeline_infos_path = Path(__file__).parent / "pipeline-infos/pipeline-infos.yaml"


def get_pipeline_infos(name: str) -> List[str]:
    infos = load_yaml(_pipeline_infos_path)
    return infos.get(name, [])


class PreflightError(Exception):
    def __init__(self, errors: Optional[str] = None):
        self.errors = errors


@dataclass
class SchemaVersion:
    """
    Create a SchemaVersion from assayclassifier and TSV data;
    if either component is missing, downstream functionality will
    likely fail.
    This assumes keys are predictable. If the rules tend to vary, we
    could add a class method like https://stackoverflow.com/q/72013377
    """

    schema_name: str  # Valid values: canonical assay name OR other type
    version: str = ""
    directory_path: Optional[Path] = None
    table_schema: Optional[str] = ""  # legacy only
    path: Path = Path()
    contributors_schemas: List[SchemaVersion] = field(default_factory=list)
    antibodies_schemas: List[SchemaVersion] = field(default_factory=list)
    rows: List = field(default_factory=list)
    soft_assay_data: Dict = field(default_factory=dict)
    is_cedar: bool = False
    dataset_type: str = ""  # String from assay_type or dataset_type field in TSV
    dir_schema: Optional[str] = None
    metadata_type: str = "assays"
    contains: List = field(default_factory=list)
    entity_type_info: Optional[EntityTypeInfo] = None
    ancestor_entities: List[AncestorTypeInfo] = field(default_factory=list)

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
        if self.schema_name in OtherTypes.with_sample_subtypes():
            self.metadata_type = "others"
        self.get_row_data()
        self.get_assayclassifier_data()
        if not self.is_cedar:
            self._get_table_schema_info()

    def get_row_data(self):
        if not self.rows:
            return
        if self.rows[0].get("metadata_schema_id"):
            self.is_cedar = True
        else:
            self.is_cedar = False
        self.get_dataset_type_value()
        if self.is_cedar:
            self.version = self.rows[0].get("metadata_schema_id")
        else:
            self.version = self.rows[0].get("version", "0")

    def get_assayclassifier_data(self):
        self.dir_schema = self.soft_assay_data.get("dir-schema")
        contains = self.soft_assay_data.get("must-contain")
        if contains:
            self.contains = [schema.lower() for schema in contains]

    def get_dataset_type_value(self):
        dataset_fields = {
            k: v for k, v in self.rows[0].items() if k in UNIQUE_FIELDS_MAP[DatasetType.DATASET]
        }
        values_found = list(dataset_fields.values())
        if len(values_found) == 0:
            return
        elif len(values_found) > 1:
            raise PreflightError(
                f"Found multiple dataset fields for path {self.path}: {dataset_fields}"
            )
        self.dataset_type = values_found[0]

    def _get_table_schema_info(self):
        if self.is_cedar:
            return
        if table_schema := self.soft_assay_data.get("tbl-schema"):
            self.table_schema = (
                table_schema
                if not table_schema.endswith("v")
                else table_schema + str(self.version)
            )
        else:
            self.table_schema = f"{self.schema_name}-v{self.version}"


@dataclass
class EntityTypeInfo:
    entity_type: EntityTypes
    entity_sub_type: str = ""
    entity_sub_type_val: str = ""

    def __post_init__(self):
        if (
            self.entity_type in [OtherTypes.SAMPLE, DatasetType.DATASET]
            and not self.entity_sub_type
        ):
            raise Exception(f"Entity of type {self.entity_type} must have a sub_type.")
        # If a member of the Sample enum is passed in as the entity_type,
        # this extracts the entity_type and entity_sub_type from that value
        # and mutates the instance accordingly
        # e.g. self.entity_type == <Sample.BLOCK: "sample-block">
        if isinstance(self.entity_type, Sample):
            self.entity_sub_type = self.entity_type.name.lower()
            self.entity_type = OtherTypes.SAMPLE
        if self.entity_sub_type == Sample.ORGAN and not self.entity_sub_type_val:
            raise Exception(
                f"Entity of type {self.entity_type}/{self.entity_sub_type} must have a sub_type_val."
            )

    def format_constraint_check_data(self) -> Dict:
        """
        Formats data about an entity so that it can be sent as
        part of the payload to the constraints endpoint.
        """
        return {
            "entity_type": self.entity_type.value,
            "sub_type": [self.entity_sub_type] if self.entity_sub_type else None,
            "sub_type_val": [self.entity_sub_type_val] if self.entity_sub_type_val else None,
        }

    def format_constraint_check_error(self):
        data_entity_sub_type = f"/{self.entity_sub_type.lower()}" if self.entity_sub_type else ""
        data_entity_sub_type_val = (
            f"/{self.entity_sub_type_val.lower()}" if self.entity_sub_type_val else ""
        )
        return self.entity_type + data_entity_sub_type + data_entity_sub_type_val


@dataclass
class AncestorTypeInfo(EntityTypeInfo):
    entity_id: Optional[str] = None
    source_schema: Optional[SchemaVersion] = None
    row: Optional[int] = None
    column: Optional[str] = None


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


def dict_directory_schema_versions() -> Dict[str, Set[str]]:
    dict_of_sets = defaultdict(set)
    for sv in list_directory_schema_versions():
        dict_of_sets[sv.dir_schema_name].add(sv.version)
    return dict_of_sets


def _get_schema_filename(schema_name: str, version: str) -> str:
    return f"{schema_name.lower()}-v{version}"


def get_table_schema(
    schema_version: SchemaVersion,
    no_url_checks: bool = False,
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
            f"No such file or directory: {_table_schemas_path}/{schema_version.metadata_type}/{schema_version.table_schema}.yaml"  # noqa: E501
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
        _add_constraints(schema_field, no_url_checks=no_url_checks, names=names)
        if schema_version.metadata_type == "assays":
            _validate_field(schema_field)

    return schema


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


def get_possible_directory_schemas(dir_schema: str) -> Optional[Dict]:
    schemas = {}
    # this assumes that versions are numbered starting at x.0, no whole numbers
    directory_schema_minor_versions = list(_directory_schemas_path.glob(f"{dir_schema}*.yaml"))
    if not directory_schema_minor_versions:
        return None
    for directory_schema_path in directory_schema_minor_versions:
        schema = load_yaml(directory_schema_path)
        schema["files"] += []
        schemas[Path(directory_schema_path).stem] = schema
    return schemas


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
     'proteomics',
     'sample',
     'sequence',
     'single_cycle_fluorescence_microscopy',
     'spatial_transcriptomics',
     'derived_datasets',
     'flow_cytometry']
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


def _add_constraints(field: dict, no_url_checks=None, names: List[str] = []) -> None:
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

    # Remove network checks if no_url_checks:
    if no_url_checks:
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
