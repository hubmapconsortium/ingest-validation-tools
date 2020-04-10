from pathlib import Path

from yaml import safe_load as load_yaml


_schemas_path = Path(__file__).parent / 'table-schemas'


def list_types():
    schemas = {p.stem for p in _schemas_path.iterdir()}
    return sorted(schemas - {'level-1'})


def get_schema(type):
    level_1_schema = load_yaml(open(_schemas_path / 'level-1.yaml').read())
    level_1_fields = level_1_schema['fields']
    type_schema = load_yaml(open(_schemas_path / f'{type}.yaml').read())
    type_fields = type_schema['fields']

    return {
        'doc_url': type_schema['doc_url'],
        'fields': level_1_fields + type_fields
    }
