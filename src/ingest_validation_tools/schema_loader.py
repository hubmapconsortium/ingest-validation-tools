from pathlib import Path
from dataclasses import dataclass
from collections import defaultdict

from ingest_validation_tools.yaml_include_loader import load_yaml


_table_schemas_path = Path(__file__).parent / 'table-schemas'
_directory_schemas_path = Path(__file__).parent / 'directory-schemas'


@dataclass
class SchemaVersion():
    '''
    >>> str(SchemaVersion('fake', 3))
    'fake-v3.yaml'

    '''
    schema_name: str
    version: int

    def __str__(self):
        return f'{self.schema_name}-v{self.version}.yaml'


def list_schema_versions():
    stems = sorted(
        p.stem for p in
        (_table_schemas_path / 'assays').iterdir()
    )
    return [
        SchemaVersion(*stem.split('-v')) for stem in stems
    ]


def dict_schema_versions():
    dict_of_sets = defaultdict(set)
    for sv in list_schema_versions():
        dict_of_sets[sv.schema_name].add(sv.version)
    return dict_of_sets


def get_other_schema(other_type, offline=None):
    schema = load_yaml(Path(__file__).parent / 'table-schemas/others' / f'{other_type}.yaml')
    for field in schema['fields']:
        _add_constraints(field, optional_fields=[], offline=offline)
    return schema


def get_table_schema(schema_name, version, optional_fields=[], offline=None):
    schema = load_yaml(_table_schemas_path / 'assays' / f'{schema_name}-v{version}.yaml')

    for field in schema['fields']:
        _add_level_1_description(field)
        _validate_level_1_enum(field)

        _add_constraints(field, optional_fields, offline=offline)
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
            'scRNAseq-10xGenomics',
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
        assert actual <= allowed, f'Unexpected enums for {name}: {actual - allowed}'


def _add_constraints(field, optional_fields, offline=None):
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
     'name': 'abc_percent',
     'type': 'number'}

    >>> field = {'name': 'optional_value'}
    >>> _add_constraints(field, ['optional_value'])
    >>> pprint(field, width=40)
    {'constraints': {'required': False},
     'name': 'optional_value',
     'type': 'number'}

    >>> field = {'name': 'whatever', 'constraints': {'pattern': 'fake-regex'}}
    >>> _add_constraints(field, [])
    >>> pprint(field, width=40)
    {'constraints': {'pattern': 'fake-regex',
                     'required': True},
     'name': 'whatever',
     'type': 'string'}

    '''
    if 'constraints' not in field:
        field['constraints'] = {}

    # Guess constraints:
    if 'required' not in field['constraints']:
        field['constraints']['required'] = True
    if 'protocols_io_doi' in field['name']:
        field['constraints']['pattern'] = r'10\.17504/.*'
        field['custom_constraints'] = {
            'url': {'prefix': 'https://dx.doi.org/'}
        }
    if field['name'].endswith('_email'):
        field['format'] = 'email'

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
