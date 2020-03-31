from pathlib import Path
import logging

from yaml import safe_load as load_yaml
from directory_schema import directory_schema
from goodtables import validate as validate_table


class TableValidationErrors(Exception):
    pass


def validate(path, type, donor_id, tissue_id):
    path_obj = Path(path)
    _validate_generic_submission(path_obj)
    _validate_dataset_directories(path_obj, type)
    _validate_metadata_tsv(path_obj / 'metadata.tsv', type.split('-')[0])


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
    datasets = [sd for sd in dir_path.iterdir() if sd.is_dir()]
    if not datasets:
        logging.warn(f'No datasets in {dir_path}')
    for sub_directory in datasets:
        logging.info(f'  Validating {sub_directory}...')
        directory_schema.validate_dir(sub_directory, schema)


def _validate_metadata_tsv(metadata_path, type):
    '''
    Validate the metadata.tsv.
    '''
    logging.info(f'Validating {type} metadata.tsv...')
    schema_path = (Path(__file__).parent
                   / 'table-schemas' / f'{type}.yaml')
    schema = load_yaml(open(schema_path).read())
    report = validate_table(metadata_path, schema=schema,
                            skip_checks=['blank-row'])

    error_messages = report['warnings']
    if 'tables' in report:
        for table in report['tables']:
            error_messages += [e['message'] for e in table['errors']]
    if error_messages:
        raise TableValidationErrors('\n\n'.join(error_messages))
