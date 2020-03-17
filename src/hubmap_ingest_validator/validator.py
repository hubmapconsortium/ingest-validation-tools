from pathlib import Path
import logging

from yaml import safe_load as load_yaml
from directory_schema import directory_schema


def validate(path, type):
    path_obj = Path(path)
    _validate_generic_submission(path_obj)
    _validate_dataset_directories(path_obj, type)


def _validate_generic_submission(path):
    '''
    Validate the directory at path.
    '''
    logging.info('Validating generic submission...')
    schema_path = Path(__file__).parent / 'schemas' / 'generic-submission.yaml'
    schema = load_yaml(open(schema_path).read())
    directory_schema.validate_dir(path, schema)


def _validate_dataset_directories(path, type):
    '''
    Validate the subdirectories under path as type.
    '''
    logging.info(f'Validating {type} submission...')
    schema_path = Path(__file__).parent / 'schemas' / 'types' / f'{type}.yaml'
    schema = load_yaml(open(schema_path).read())
    for sub_directory in [sd for sd in path.iterdir() if sd.is_dir()]:
        logging.info(f'  Validating {sub_directory}...')
        directory_schema.validate_dir(sub_directory, schema)
