from __future__ import annotations

import os
from pathlib import Path
from collections import defaultdict, namedtuple
from copy import deepcopy
import re
from typing import List, Dict, Any, Set, Sequence, Optional, Union

from ingest_validation_tools.yaml_include_loader import load_yaml
from ingest_validation_tools.enums import shared_enums


_table_schemas_path = Path(__file__).parent / "table-schemas"
_directory_schemas_path = Path(__file__).parent / "directory-schemas"
_pipeline_infos_path = Path(__file__).parent / "pipeline-infos/pipeline-infos.yaml"


def get_pipeline_infos(name: str) -> List[str]:
    infos = load_yaml(_pipeline_infos_path)
    return infos.get(name, [])


class PreflightError(Exception):
    pass


SchemaVersion = namedtuple("SchemaVersion", ["schema_name", "version"])


def get_fields_wo_headers(schema: dict) -> List[dict]:
    return [field for field in schema["fields"] if not isinstance(field, str)]


def get_field_enum(field_name: str, schema: dict) -> List[str]:
    fields_wo_headers = get_fields_wo_headers(schema)
    fields = [field for field in fields_wo_headers if field["name"] == field_name]
    if not fields:
        return []
    assert len(fields) == 1
    return fields[0]["constraints"]["enum"]


def get_table_schema_version_from_row(
    path: str, row: Dict[str, Any], cedar_validation: bool = True
) -> SchemaVersion:
    from ingest_validation_tools.validation_utils import get_other_names

    """
    >>> try: get_table_schema_version_from_row('empty', {'bad-column': 'bad-value'})
    ... except Exception as e: print(e)
    empty does not contain "assay_type" or "dataset_type". Column headers: bad-column

    >>> get_table_schema_version_from_row( \
            'v0', \
            {'assay_type': 'PAS microscopy'}, \
            cedar_validation=False \
        )
    SchemaVersion(schema_name='stained', version='0')

    >>> try: get_table_schema_version_from_row('v42', \
                {'assay_type': 'PAS microscopy', 'version': 42}, \
                cedar_validation=False \
                )
    ... except PreflightError as e: print(e)
    No schema where 'PAS microscopy' is assay_type and 42 is version

    """
    assay = row["assay_type"] if "assay_type" in row else row.get("dataset_type")
    source_project = row["source_project"] if "source_project" in row else None
    dir = "assays"

    if not cedar_validation:
        version = row["version"] if "version" in row else "0"
    else:
        version = "cedar"

    other_type = [
        other_type
        for other_type in get_other_names()
        if f"{other_type}_id" in row.keys()
    ]
    if other_type:
        assay = other_type[0]
        dir = "others"
    elif not assay:
        message = f'{path} does not contain "assay_type" or "dataset_type". '
        if "channel_id" in row:
            message += (
                'Has "channel_id": Antibodies TSV found where metadata TSV expected.'
            )
        elif "orcid_id" in row:
            message += (
                'Has "orcid_id": Contributors TSV found where metadata TSV expected.'
            )
        else:
            message += f'Column headers: {", ".join(row.keys())}'
        raise PreflightError(message)

    schema_names = _assay_to_schema_name(assay, version, source_project, dir=dir)

    for schema_name in schema_names:
        if not cedar_validation:
            schema_path = (
                _table_schemas_path / dir / _get_schema_filename(schema_name, version)
            )
            if Path(schema_path).exists():
                return SchemaVersion(schema_name, version)
        else:
            cedar_schema = _get_cedar_schema(schema_name, assay, version, dir=dir)
            if cedar_schema:
                return cedar_schema
    message = f"No schema where '{assay}' is assay_type and {version} is version"
    raise PreflightError(message)


def _get_cedar_schema(
    schema_name: str, assay: str, version: Union[str, int], dir: str
) -> Union[SchemaVersion, None]:
    """
    This will return the highest numbered schema matching is_cedar.
    """
    dir_path = _table_schemas_path / dir
    schema_files = [
        f"{dir_path}/{schema_file}"
        for schema_file in os.listdir(dir_path)
        if schema_file.startswith(schema_name.lower())
    ]
    for schema_path in schema_files:
        schema = load_yaml(Path(schema_path))
        fields = get_fields_wo_headers(schema)
        cedar_field = [field for field in fields if field["name"] == "is_cedar"]
        if not cedar_field:
            continue
        filename = Path(schema_path).name
        version_regex = re.compile(r"\d+")
        version_group = version_regex.search(filename)
        if version_group:
            version = version_group[0]
        assay_type_enums = [
            field["constraints"]["enum"]
            for field in fields
            if field["name"] == "assay_type"
        ][0]
        assert assay.lower() in [
            enum.lower() for enum in assay_type_enums
        ], f"""
            Assay type '{assay}' does not match any assay type in
            enum '{assay_type_enums}' for schema {schema_path}
            """
        return SchemaVersion(schema_name, version)
    return None


def _assay_to_schema_name(
    assay_type: str, version: str, source_project: Union[str, None], dir: str = "assays"
) -> List[str]:
    """
    Given an assay name, and a source_project (may be None),
    read all the schemas until one matches.
    Return the schema name, but not the version.

    >>> _assay_to_schema_name('PAS microscopy', '1', None)
    ['stained']

    >>> _assay_to_schema_name('snRNAseq', '1', None)
    ['scrnaseq']

    >>> _assay_to_schema_name('snRNAseq', '1', 'HCA')
    ['scrnaseq-hca']


    Or, if a match can not be found (try-except just for shorter lines):

    >>> try:  _assay_to_schema_name('PAS microscopy', '1', 'HCA')
    ... except PreflightError as e: print(e)
    No schema where 'PAS microscopy' is assay_type and 'HCA' is source_project

    >>> try: _assay_to_schema_name('snRNAseq', '1', 'Bad Project')
    ... except PreflightError as e: print(e)
    No schema where 'snRNAseq' is assay_type and 'Bad Project' is source_project

    >>> try: _assay_to_schema_name('Bad assay', '1', None)
    ... except PreflightError as e: print(e)
    No schema where 'Bad assay' is assay_type

    >>> try: _assay_to_schema_name('Bad assay', '1', 'HCA')
    ... except PreflightError as e: print(e)
    No schema where 'Bad assay' is assay_type and 'HCA' is source_project

    """
    assay_names = []
    for path in (Path(__file__).parent / "table-schemas" / dir).glob("*.yaml"):
        schema = load_yaml(path)
        assay_type_enum = get_field_enum("assay_type", schema)

        # TODO: idiosyncratic handling of case for matching with enums
        if assay_type.lower() not in [assay.lower() for assay in assay_type_enum]:
            continue

        is_cedar = False
        for field in schema.get("fields", []):
            if type(field) == dict and field.get("name", "") == "is_cedar":
                is_cedar = True

        if is_cedar and version == "cedar":
            assay_names.append(assay_type)
        else:
            source_project_enum = get_field_enum("source_project", schema)

            if source_project_enum:
                if not source_project:
                    continue

            if source_project:
                if not source_project_enum:
                    continue
                if source_project not in source_project_enum:
                    continue

            v_match = re.match(r".+(?=-v\d+)", path.stem)
            if not v_match:
                raise PreflightError(f"No version in {path}")
            assay_names.append(v_match[0])

    if assay_names:
        return list(set(assay_names))

    message = f"No schema where '{assay_type}' is assay_type"
    if source_project is not None:
        message += f" and '{source_project}' is source_project"
    raise PreflightError(message)


def list_table_schema_versions() -> List[SchemaVersion]:
    """
    >>> list_table_schema_versions()[0]
    SchemaVersion(schema_name='10x-multiome', version='2')

    """
    schema_paths = list((_table_schemas_path / "assays").iterdir()) + list(
        (_table_schemas_path / "others").iterdir()
    )
    stems = sorted(p.stem for p in schema_paths if p.suffix == ".yaml")
    v_matches = [re.match(r"(.+)-v(\d+)", stem) for stem in stems]
    if not all(v_matches):
        raise Exception(f"All YAML should have version: {stems}")
    return [SchemaVersion(*v_match.groups()) for v_match in v_matches if v_match]


def dict_table_schema_versions() -> Dict[str, Set[str]]:
    """
    >>> sorted(dict_table_schema_versions()['af'])
    ['0', '1', '2']
    """

    dict_of_sets = defaultdict(set)
    for sv in list_table_schema_versions():
        dict_of_sets[sv.schema_name].add(sv.version)
    return dict_of_sets


def list_directory_schema_versions() -> List[SchemaVersion]:
    """
    >>> list_directory_schema_versions()[0]
    SchemaVersion(schema_name='10x-multiome', version='2')

    """
    schema_paths = list(_directory_schemas_path.iterdir())
    stems = sorted(p.stem for p in schema_paths if p.suffix == ".yaml")
    return [SchemaVersion(*_parse_schema_version(stem)) for stem in stems]


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


def get_all_directory_schema_versions(schema_name: str) -> List[SchemaVersion]:
    return [
        version
        for version in list_directory_schema_versions()
        if version.schema_name == schema_name
    ]


def dict_directory_schema_versions() -> Dict[str, Set[str]]:
    dict_of_sets = defaultdict(set)
    for sv in list_directory_schema_versions():
        dict_of_sets[sv.schema_name].add(sv.version)
    return dict_of_sets


def _get_schema_filename(schema_name: str, version: str) -> str:
    return f"{schema_name.lower()}-v{version}.yaml"


def get_other_schema(
    schema_name: str, version: str, offline=None, keep_headers: bool = False
) -> dict:
    schema = load_yaml(
        _table_schemas_path / "others" / _get_schema_filename(schema_name, version)
    )
    fields_wo_headers = get_fields_wo_headers(schema)
    if not keep_headers:
        schema["fields"] = fields_wo_headers

    names = [field["name"] for field in fields_wo_headers]
    for field in schema["fields"]:
        if isinstance(field, str):
            continue
        _add_constraints(field, optional_fields=[], offline=offline, names=names)
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


def get_table_schema(
    schema_name: str,
    version: str,
    optional_fields: List[str] = [],
    offline=None,
    keep_headers: bool = False,
) -> dict:
    schema = load_yaml(
        _table_schemas_path / "assays" / _get_schema_filename(schema_name, version)
    )
    fields_wo_headers = get_fields_wo_headers(schema)
    if not keep_headers:
        schema["fields"] = fields_wo_headers

    names = [field["name"] for field in fields_wo_headers]
    for field in schema["fields"]:
        if isinstance(field, str):
            continue
        _add_level_1_description(field)
        _validate_level_1_enum(field)

        _add_constraints(field, optional_fields, offline=offline, names=names)
        _validate_field(field)

    return schema


def get_directory_schema(directory_type: str, schema_version: str) -> Optional[dict]:
    directory_schema_path = _directory_schemas_path / _get_schema_filename(
        directory_type, schema_version
    )
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
        optional = not field["constraints"].get(
            "required", True
        )  # Default: required = True
        actual = set(
            field["constraints"].get(
                "enum",
                [] if optional else None
                # Only optional fields are allowed to skip the enum.
            )
        )
        allowed = set(shared_enums[name])
        assert actual <= allowed, (
            f"Unexpected enums for {name}: {actual - allowed}\n"
            f"Allowed: {sorted(allowed)}"
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
    for field in original_fields:
        extra_field = None
        if "constraints" in field:
            constraints = field["constraints"]
            if "enum" in constraints:
                if isinstance(constraints["enum"], dict):
                    constraints["enum"] = list(constraints["enum"].keys())
                    if add_none_of_the_above:
                        constraints["enum"].append("Submitter Suggestion")
                    if add_suggested:
                        extra_field = {
                            "name": f"{field['name']}_suggested",
                            "description": f"Desired value for {field['name']}",
                        }
        schema_copy["fields"].append(field)
        if extra_field:
            schema_copy["fields"].append(extra_field)
    return schema_copy
