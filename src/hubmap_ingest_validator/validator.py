from pathlib import Path
import logging
import csv

from yaml import safe_load as load_yaml
from directory_schema import directory_schema
from goodtables import validate as validate_table

from hubmap_ingest_validator.table_schemas import get_schema


class TableValidationErrors(Exception):
    pass


def validate(path, type, donor_id, tissue_id):
    path_obj = Path(path)
    _validate_generic_submission(path_obj)
    _validate_dataset_directories(path_obj, type)
    _validate_metadata_tsv(path_obj / 'metadata.tsv', type.split('-')[0])
    _validate_references_up(path_obj / 'metadata.tsv', donor_id, tissue_id)


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
    schema = get_schema(type)
    report = validate_table(metadata_path, schema=schema,
                            skip_checks=['blank-row'])

    error_messages = report['warnings']
    if 'tables' in report:
        for table in report['tables']:
            error_messages += [e['message'] for e in table['errors']]
    if error_messages:
        raise TableValidationErrors('\n\n'.join(error_messages))


def _validate_references_up(metadata_path, donor_id, tissue_id):
    logging.info(f'Validating donor_id and tissue_id...')
    with open(metadata_path) as tsv:
        reader = csv.DictReader(tsv, delimiter='\t')
        error_messages = []
        for i, row in enumerate(reader):
            if donor_id != row['donor_id']:
                error_messages.append(
                    f'On row {i+1}, donor_id is "{row["donor_id"]}"')
            if tissue_id != row['tissue_id']:
                error_messages.append(
                    f'On row {i+1}, tissue_id is "{row["tissue_id"]}"')
    if error_messages:
        raise TableValidationErrors('\n'.join(error_messages))
