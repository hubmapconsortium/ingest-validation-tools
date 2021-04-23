from pathlib import Path
from collections import (defaultdict, namedtuple)
import re

from ingest_validation_tools.yaml_include_loader import load_yaml


_table_schemas_path = Path(__file__).parent / 'table-schemas'
_directory_schemas_path = Path(__file__).parent / 'directory-schemas'


class PreflightError(Exception):
    pass


SchemaVersion = namedtuple('SchemaVersion', ['schema_name', 'version'])


def get_schema_version_from_row(path, row):
    '''
    >>> get_schema_version_from_row('empty', {'bad-column': 'bad-value'})
    Traceback (most recent call last):
    ...
    schema_loader.PreflightError: empty does not contain "assay_type". Column headers: bad-column

    >>> get_schema_version_from_row('v0', {'assay_type': 'PAS microscopy'})
    SchemaVersion(schema_name='stained', version=0)

    >>> get_schema_version_from_row('v42', {'assay_type': 'PAS microscopy', 'version': 42})
    SchemaVersion(schema_name='stained', version=42)

    '''
    if 'assay_type' not in row:
        message = f'{path} does not contain "assay_type". '
        if 'channel_id' in row:
            message += 'Has "channel_id": Antibodies TSV found where metadata TSV expected.'
        elif 'orcid_id' in row:
            message += 'Has "orcid_id": Contributors TSV found where metadata TSV expected.'
        else:
            message += f'Column headers: {", ".join(row.keys())}'
        raise PreflightError(message)

    assay = row['assay_type']
    source_project = row['source_project'] if 'source_project' in row else None
    schema_name = _assay_to_schema_name(assay, source_project)

    version = row['version'] if 'version' in row else 0
    return SchemaVersion(schema_name, version)


def _assay_to_schema_name(assay_type, source_project):
    '''
    Given an assay name, and a source_project (may be None),
    read all the schemas until one matches.
    Return the schema name, but not the version.

    >>> _assay_to_schema_name('PAS microscopy', None)
    'stained'

    >>> _assay_to_schema_name('snRNAseq', None)
    'scrnaseq'

    >>> _assay_to_schema_name('snRNAseq', 'HCA')
    'scrnaseq-hca'


    Or, if a match can not be found (try-except just for shorter lines):

    >>> try:
    ...    _assay_to_schema_name('PAS microscopy', 'HCA')
    ... except PreflightError as e:
    ...    print(e)
    No schema where 'PAS microscopy' is assay_type and 'HCA' is source_project

    >>> try:
    ...    _assay_to_schema_name('snRNAseq', 'Bad Project')
    ... except PreflightError as e:
    ...    print(e)
    No schema where 'snRNAseq' is assay_type and 'Bad Project' is source_project

    >>> try:
    ...    _assay_to_schema_name('Bad assay', None)
    ... except PreflightError as e:
    ...    print(e)
    No schema where 'Bad assay' is assay_type

    >>> try:
    ...    _assay_to_schema_name('Bad assay', 'HCA')
    ... except PreflightError as e:
    ...    print(e)
    No schema where 'Bad assay' is assay_type and 'HCA' is source_project

    '''
    for path in (Path(__file__).parent / 'table-schemas' / 'assays').glob('*.yaml'):
        schema = load_yaml(path)

        assay_type_fields = [f for f in schema['fields'] if f['name'] == 'assay_type']
        source_project_fields = [f for f in schema['fields'] if f['name'] == 'source_project']

        if assay_type not in assay_type_fields[0]['constraints']['enum']:
            continue

        if source_project_fields:
            if not source_project:
                continue

        if source_project:
            if not source_project_fields:
                continue
            if source_project not in source_project_fields[0]['constraints']['enum']:
                continue

        return re.match(r'.+(?=-v\d+)', path.stem)[0]

    message = f"No schema where '{assay_type}' is assay_type"
    if source_project is not None:
        message += f" and '{source_project}' is source_project"
    raise PreflightError(message)


def list_schema_versions():
    '''
    >>> list_schema_versions()[0]
    SchemaVersion(schema_name='af', version='0')

    '''
    schema_paths = list((_table_schemas_path / 'assays').iterdir()) + \
        list((_table_schemas_path / 'others').iterdir())
    stems = sorted(p.stem for p in schema_paths)
    return [
        SchemaVersion(*re.match(r'(.+)-v(\d+)', stem).groups()) for stem in stems
    ]


def dict_schema_versions():
    dict_of_sets = defaultdict(set)
    for sv in list_schema_versions():
        dict_of_sets[sv.schema_name].add(sv.version)
    return dict_of_sets


def _get_schema_filename(schema_name, version):
    return f'{schema_name}-v{version}.yaml'


def get_other_schema(schema_name, version, offline=None):
    schema = load_yaml(
        _table_schemas_path / 'others' /
        _get_schema_filename(schema_name, version))
    names = [field['name'] for field in schema['fields']]
    for field in schema['fields']:
        _add_constraints(field, optional_fields=[], offline=offline, names=names)
    return schema


def get_is_assay(schema_name):
    # TODO: read from file system... but larger refactor may make it redundant.
    return schema_name not in ['donor', 'sample', 'antibodies', 'contributors']


def get_table_schema(schema_name, version, optional_fields=[], offline=None):
    schema = load_yaml(
        _table_schemas_path / 'assays' /
        _get_schema_filename(schema_name, version))

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
            f'Allowed: {sorted(allowed)}'


def _add_constraints(field, optional_fields, offline=None, names=None):
    '''
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
     'custom_constraints': {'sequence_limit': 3},
     'name': 'abc_percent',
     'type': 'number'}

    Fields can be made optional at run-time:

    >>> field = {'name': 'optional_value'}
    >>> _add_constraints(field, ['optional_value'])
    >>> pprint(field, width=40)
    {'constraints': {'required': False},
     'custom_constraints': {'sequence_limit': 3},
     'name': 'optional_value',
     'type': 'number'}

    Default field type is string:

    >>> field = {'name': 'whatever', 'constraints': {'pattern': 'fake-regex'}}
    >>> _add_constraints(field, [])
    >>> pprint(field, width=40)
    {'constraints': {'pattern': 'fake-regex',
                     'required': True},
     'custom_constraints': {'sequence_limit': 3},
     'name': 'whatever',
     'type': 'string'}

    Some fields are expected to have sequential numbers:

    >>> field = {'name': 'channel_id'}
    >>> _add_constraints(field, [])
    >>> pprint(field, width=40)
    {'constraints': {'required': True},
     'custom_constraints': {},
     'name': 'channel_id'}

    '''
    if 'constraints' not in field:
        field['constraints'] = {}
    if 'custom_constraints' not in field:
        field['custom_constraints'] = {}

    # Guess constraints:
    if 'required' not in field['constraints']:
        field['constraints']['required'] = True
    if 'protocols_io_doi' in field['name']:
        field['constraints']['pattern'] = r'10\.17504/.*'
        field['custom_constraints']['url'] = {'prefix': 'https://dx.doi.org/'}
    if field['name'].endswith('_email'):
        field['format'] = 'email'
    if field['name'] != 'channel_id':
        field['custom_constraints']['sequence_limit'] = 3
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
