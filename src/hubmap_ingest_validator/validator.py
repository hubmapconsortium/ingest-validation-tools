from pathlib import Path
import os

from yaml import safe_load as load_yaml
from directory_schema import directory_schema


def validate(path, type):
    _validate_generic_submission(path)
    _validate_dataset_directories(path, type)

def _validate_generic_submission(path):
    '''
    Validate the directory at path.
    '''
    schema_path = Path(__file__).parent / 'schemas' / 'generic-submission.yaml'
    schema = load_yaml(open(schema_path).read())
    directory_schema.validate_dir(path, schema)

def _validate_dataset_directories(path, type):
    '''
    Validate the subdirectories under path as type.
    '''
    schema_path = Path(__file__).parent / 'schemas' / 'types' / f'{type}.yaml'
    schema = load_yaml(open(schema_path).read())
    for sub_directory in [f for f in os.listdir(path) if os.path.isdir(f)]:
        directory_schema.validate_dir(sub_directory, schema)
