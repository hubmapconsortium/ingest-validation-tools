from pathlib import Path

from yaml import safe_load as load_yaml


_schemas_path = Path(__file__).parent / 'table-schemas'


def list_types():
    schemas = {p.stem for p in _schemas_path.iterdir()}
    return schemas - {'level-1'}


def get_schema(type):
    level_1_fields = load_yaml(open(_schemas_path / 'level-1.yaml').read())
    type_fields = load_yaml(open(_schemas_path / f'{type}.yaml').read())

    return {
        'fields': level_1_fields + type_fields
    }
