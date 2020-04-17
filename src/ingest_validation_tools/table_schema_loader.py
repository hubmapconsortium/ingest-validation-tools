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

    fields = level_1_fields + type_fields + paths_fields
    for field in fields:
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

    return {
        'doc_url': type_schema['doc_url'],
        'fields': fields
    }


def _get_sub_schema(type):
    return load_yaml(open(_schemas_path / f'{type}.yaml').read())
