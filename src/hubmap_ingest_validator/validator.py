from pathlib import Path

from yaml import safe_load as load_yaml
from directory_schema import directory_schema


def validate(path, type):
    '''
    Validate the directory at path as type.
    '''
    schema_path = Path(__file__).parent / 'schemas' / 'generic-ingest-directory.yaml'
    schema = load_yaml(open(schema_path).read())
    directory_schema.validate_dir(path, schema)
