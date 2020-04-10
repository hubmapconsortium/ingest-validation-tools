from pathlib import Path

from yaml import safe_load as load_yaml


_schemas_path = Path(__file__).parent / 'table-schemas'


def list_types():
    schemas = {p.stem for p in _schemas_path.iterdir()}
    return sorted(schemas - {'level-1', 'paths'})


def get_schema(type):
    level_1_fields = _get_sub_schema('level-1')['fields']
    paths_fields = _get_sub_schema('paths')['fields']
    type_schema = _get_sub_schema(type)
    type_fields = type_schema['fields']

    fields = level_1_fields + type_fields + paths_fields
    for field in fields:
        if 'constraints' not in field:
            field['constraints'] = {}
        if 'required' not in field['constraints']:
            field['constraints']['required'] = True
        if 'percent' in field['name']:
            field['type'] = 'number'
            field['constraints'] = {
                'minimum': 0,
                'maximum': 100
            }

    return {
        'doc_url': type_schema['doc_url'],
        'fields': fields
    }


def _get_sub_schema(type):
    return load_yaml(open(_schemas_path / f'{type}.yaml').read())
