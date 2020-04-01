from pathlib import Path

from yaml import safe_load as load_yaml


_schemas_path = Path(__file__).parent / 'table-schemas'


def list_types():
    schemas = {p.stem for p in _schemas_path.iterdir()}
    return schemas - {'level-1'}


def get_schema(type):
    schema_path = _schemas_path / f'{type}.yaml'
    specific_schema = load_yaml(open(schema_path).read())

    level_1_fields = load_yaml(open(_schemas_path / 'level-1.yaml').read())

    specific_schema['fields'] = level_1_fields + specific_schema['fields']
    return specific_schema
