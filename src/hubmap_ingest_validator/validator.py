from pathlib import Path
import logging

from yaml import safe_load as load_yaml
from directory_schema import directory_schema


def validate(path, type):
    path_obj = Path(path)
    _validate_generic_submission(path_obj)
    _validate_dataset_directories(path_obj, type)
    _validate_metadata_csv(path_obj / 'metadata.txt')


def _validate_generic_submission(dir_path):
    '''
    Validate the directory at path.
    '''
    logging.info('Validating generic submission...')
    schema_path = (Path(__file__).parent
                   / 'directory-schemas' / 'submission.yaml')
    schema = load_yaml(open(schema_path).read())
    directory_schema.validate_dir(dir_path, schema)


def _validate_dataset_directories(dir_path, type):
    '''
    Validate the subdirectories under path as type.
    '''
    logging.info(f'Validating {type} submission...')
    schema_path = (Path(__file__).parent
                   / 'directory-schemas' / 'datasets' / f'{type}.yaml')
    schema = load_yaml(open(schema_path).read())
    for sub_directory in [sd for sd in dir_path.iterdir() if sd.is_dir()]:
        logging.info(f'  Validating {sub_directory}...')
        directory_schema.validate_dir(sub_directory, schema)


def _validate_metadata_csv(metadata_path):
    pass
