from pathlib import Path
from collections import (defaultdict, namedtuple)
from copy import deepcopy

from ingest_validation_tools.yaml_include_loader import load_yaml


_table_schemas_path = Path(__file__).parent / 'table-schemas'
_directory_schemas_path = Path(__file__).parent / 'directory-schemas'


SchemaVersion = namedtuple('SchemaVersion', ['schema_name', 'version'])


def list_schema_versions():
    schema_paths = list((_table_schemas_path / 'assays').iterdir()) + \
        list((_table_schemas_path / 'others').iterdir())
    stems = sorted(p.stem for p in schema_paths)
    return [
        SchemaVersion(*stem.split('-v')) for stem in stems
    ]


def dict_schema_versions():
    dict_of_sets = defaultdict(set)
    for sv in list_schema_versions():
        dict_of_sets[sv.schema_name].add(sv.version)
    return dict_of_sets


def _get_schema_filename(schema_name, version, source_project):
    dash_source = f"-{source_project.lower().replace(' ', '_')}" if source_project else ''
    dash_version = f'-v{version}'
    return f'{schema_name}{dash_source}{dash_version}.yaml'


def get_other_schema(schema_name, version, source_project=None, offline=None):
    schema = load_yaml(
        _table_schemas_path / 'others' /
        _get_schema_filename(schema_name, version, source_project))
    names = [field['name'] for field in schema['fields']]
    for field in schema['fields']:
        _add_constraints(field, optional_fields=[], offline=offline, names=names)
    return schema


def get_is_assay(schema_name):
    # TODO: read from file system... but larger refactor may make it redundant.
    return schema_name not in ['donor', 'sample', 'antibodies', 'contributors']


def get_table_schema(schema_name, version, source_project=None, optional_fields=[], offline=None):
    schema = load_yaml(
        _table_schemas_path / 'assays' /
        _get_schema_filename(schema_name, version, source_project))

    names = [field['name'] for field in schema['fields']]
    for field in schema['fields']:
        _add_level_1_description(field)
        _validate_level_1_enum(field)

        _add_constraints(field, optional_fields, offline=offline, names=names)
        _validate_field(field)

    return schema


def get_directory_schema(directory_type):
    schema = load_yaml(_directory_schemas_path / f'{directory_type}.yaml')
    schema += [
        {
            'pattern': r'extras/.*',
            'description': 'Free-form descriptive information supplied by the TMC',
            'required': False
        },
        {
            'pattern': r'extras/thumbnail\.(png|jpg)',
            'description': 'Optional thumbnail image which may be shown in search interface',
            'required': False
        }
    ]
    return schema


def _validate_field(field):
    if field['name'].endswith('_unit') and 'enum' not in field['constraints']:
        raise Exception('"_unit" fields must have enum constraints', field)


def _add_level_1_description(field):
    descriptions = {
        'assay_category': 'Each assay is placed into one of the following 3 general categories: '
        'generation of images of microscopic entities, identification & quantitation of molecules '
        'by mass spectrometry, and determination of nucleotide sequence.',
        'assay_type': 'The specific type of assay being executed.',
        'analyte_class': 'Analytes are the target molecules being measured with the assay.',
    }
    name = field['name']
    if name in descriptions:
        field['description'] = descriptions[name]


def _validate_level_1_enum(field):
    enums = {
        'assay_category': [
            'imaging',
            'mass_spectrometry',
            'mass_spectrometry_imaging',
            'sequence'
        ],
        'assay_type': [
            '3D Imaging Mass Cytometry',
            'scRNA-Seq(10xGenomics)',
            'AF',
            'bulk RNA',
            'bulkATACseq',
            'Cell DIVE',
            'CODEX',
            'Imaging Mass Cytometry',
            'LC-MS (metabolomics)',
            'LC-MS/MS (label-free proteomics)',
            'Light Sheet',
            'MxIF',
            'MALDI-IMS',
            'MS (shotgun lipidomics)',
            'NanoDESI',
            'NanoPOTS',
            'PAS microscopy',
            'scATACseq',
            'sciATACseq',
            'sciRNAseq',
            'seqFISH',
            'SNARE-seq2',
            'snATACseq',
            'snRNA',
            'SPLiT-Seq',
            'TMT (proteomics)',
            'WGS',
            'SNARE2-RNAseq',
            'snRNAseq',
            'scRNAseq-10xGenomics',  # Only needed for scrnaseq-v0.yaml.
            'scRNAseq-10xGenomics-v2',
            'scRNAseq-10xGenomics-v3',
            'scRNAseq',
            'Slide-seq'
        ],
        'analyte_class': [
            'DNA',
            'RNA',
            'protein',
            'lipids',
            'metabolites',
            'polysaccharides',
            'metabolites_and_lipids'
        ]
    }
    name = field['name']
    if name in enums:
        actual = set(field['constraints']['enum']) if 'enum' in field['constraints'] else set()
        allowed = set(enums[name])
        assert actual <= allowed, f'Unexpected enums for {name}: {actual - allowed}\n' \
            'Allowed: {sorted(allowed)}'


def _add_constraints(field, optional_fields, offline=None, names=None):
    '''
    Modifies field in-place, adding implicit constraints
    based on the field name.

    >>> from pprint import pprint
    >>> field = {'name': 'abc_percent'}
    >>> _add_constraints(field, [])
    >>> pprint(field, width=40)
    {'constraints': {'maximum': 100,
                     'minimum': 0,
                     'required': True},
     'custom_constraints': {'sequence_limit': 3},
     'name': 'abc_percent',
     'type': 'number'}

    >>> field = {'name': 'optional_value'}
    >>> _add_constraints(field, ['optional_value'])
    >>> pprint(field, width=40)
    {'constraints': {'required': False},
     'custom_constraints': {'sequence_limit': 3},
     'name': 'optional_value',
     'type': 'number'}

    >>> field = {'name': 'whatever', 'constraints': {'pattern': 'fake-regex'}}
    >>> _add_constraints(field, [])
    >>> pprint(field, width=40)
    {'constraints': {'pattern': 'fake-regex',
                     'required': True},
     'custom_constraints': {'sequence_limit': 3},
     'name': 'whatever',
     'type': 'string'}

    '''
    if 'constraints' not in field:
        field['constraints'] = {}
    if 'custom_constraints' not in field:
        field['custom_constraints'] = {}

    # For all fields:
    field['custom_constraints']['sequence_limit'] = 3

    # Guess constraints:
    if 'required' not in field['constraints']:
        field['constraints']['required'] = True
    if 'protocols_io_doi' in field['name']:
        field['constraints']['pattern'] = r'10\.17504/.*'
        field['custom_constraints']['url'] = {'prefix': 'https://dx.doi.org/'}
    if field['name'].endswith('_email'):
        field['format'] = 'email'
    if field['name'].endswith('_unit'):
        # Issues have been filed to make names more consistent:
        # https://github.com/hubmapconsortium/ingest-validation-tools/issues/645
        # https://github.com/hubmapconsortium/ingest-validation-tools/issues/646
        for suffix in ['_value', '']:
            target = field['name'].replace('_unit', suffix)
            if target in names:
                break
        if target in names:
            field['custom_constraints']['units_for'] = target
            field['constraints']['required'] = False

    # Guess types:
    if field['name'].startswith('is_'):
        field['type'] = 'boolean'
    if field['name'].endswith('_value'):
        field['type'] = 'number'
    if field['name'].startswith('number_of_'):
        field['type'] = 'integer'
    if 'percent' in field['name']:
        field['type'] = 'number'
        field['constraints']['minimum'] = 0
        field['constraints']['maximum'] = 100
    if 'pattern' in field['constraints']:
        field['type'] = 'string'

    # Override:
    if field['name'] in optional_fields:
        field['constraints']['required'] = False

    # Remove network checks if offline:
    if offline:
        c_c = 'custom_constraints'
        if c_c in field and 'url' in field[c_c]:
            del field[c_c]['url']


def enum_maps_to_lists(schema, add_none_of_the_above=False, add_suggested=False):
    '''
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
                                          'None of the above']},
                 'name': 'ice_cream'},
                {'constraints': {'enum': ['happy', 'sad']}, 'name': 'mood'},
                {'constraints': {}, 'name': 'no_enum'},
                {'name': 'no_constraints'}],
     'whatever': 'is preserved'}

    >>> pprint(enum_maps_to_lists(schema, add_none_of_the_above=True, add_suggested=True))
    {'fields': [{'constraints': {'enum': ['vanilla',
                                          'chocolate',
                                          'None of the above']},
                 'name': 'ice_cream'},
                {'description': 'Desired value for ice_cream',
                 'name': 'ice_cream_suggested'},
                {'constraints': {'enum': ['happy', 'sad']}, 'name': 'mood'},
                {'constraints': {}, 'name': 'no_enum'},
                {'name': 'no_constraints'}],
     'whatever': 'is preserved'}
    '''
    schema_copy = deepcopy(schema)
    schema_copy['fields'], original_fields = \
        [], schema_copy['fields']
    for field in original_fields:
        extra_field = None
        if 'constraints' in field:
            constraints = field['constraints']
            if 'enum' in constraints:
                if isinstance(constraints['enum'], dict):
                    constraints['enum'] = list(constraints['enum'].keys())
                    if add_none_of_the_above:
                        constraints['enum'].append('None of the above')
                    if add_suggested:
                        extra_field = {
                            'name': f"{field['name']}_suggested",
                            'description': f"Desired value for {field['name']}"
                        }
        schema_copy['fields'].append(field)
        if extra_field:
            schema_copy['fields'].append(extra_field)
    return schema_copy
