from pathlib import Path

from yaml import safe_load as load_yaml


_schemas_path = Path(__file__).parent / 'table-schemas'


def list_types():
    schemas = {p.stem for p in _schemas_path.iterdir()}
    return sorted(schemas - {'level-1', 'paths', 'README'})


def get_schema(type, optional_fields=[]):
    table_type = type.split('-')[0]

    level_1_fields = _get_sub_schema('level-1')['fields']
    paths_fields = _get_sub_schema('paths')['fields']
    type_schema = _get_sub_schema(table_type)
    type_fields = type_schema['fields']

    level_1_field_names = {field['name'] for field in level_1_fields}
    type_field_names = {field['name'] for field in type_fields}
    override_field_names = set.intersection(
        level_1_field_names, type_field_names)

    level_1_fields_plus_overrides = [
        # TODO: Actually override!
        (field if field['name'] in override_field_names else field)
        for field in level_1_fields
    ]
    type_fields_minus_overrides = [
        field for field in type_fields
        if field['name'] not in override_field_names
    ]

    fields = (
        level_1_fields_plus_overrides
        + type_fields_minus_overrides
        + paths_fields
    )
    for field in fields:
        _add_constraints(field, optional_fields)
    return {
        'doc_url': type_schema['doc_url'],
        'fields': fields
    }


def _get_sub_schema(type):
    return load_yaml(open(_schemas_path / f'{type}.yaml').read())


def _add_constraints(field, optional_fields):
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

    '''
    if 'constraints' not in field:
        field['constraints'] = {}

    # Guess constraints:
    if 'required' not in field['constraints']:
        field['constraints']['required'] = True
    if 'protocols_io_doi' in field['name']:
        field['constraints']['pattern'] = r'10\.17504/.*'
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

    # Override:
    if field['name'] in optional_fields:
        field['constraints']['required'] = False
