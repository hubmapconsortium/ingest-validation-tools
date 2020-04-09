from pathlib import Path
import logging
import csv
import re
from string import ascii_uppercase

from yaml import safe_load as load_yaml
from directory_schema import directory_schema
from goodtables import validate as validate_table

from hubmap_ingest_validator.table_schemas import get_schema


class TableValidationErrors(Exception):
    pass


def validate(path, type, skip_data_path=False):
    path_obj = Path(path)
    _validate_generic_submission(path_obj)
    _validate_dataset_directories(path_obj, type)
    validate_metadata_tsv(path_obj / 'metadata.tsv', type.split('-')[0])
    if not skip_data_path:
        _validate_references_down(path_obj)


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


def validate_metadata_tsv(metadata_path, type):
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
            error_messages += [
                _column_number_to_letters(e['message'])
                for e in table['errors']
            ]
    if error_messages:
        raise TableValidationErrors('\n\n'.join(error_messages))


def _column_number_to_letters(message):
    return re.sub(
        r'(column) (\d+)',
        lambda m: f'{m[1]} {m[2]} ("{_number_to_letters(m[2])}")',
        message,
        flags=re.I
    )


def _number_to_letters(n):
    '''
    >>> _number_to_letters(1)
    'A'
    >>> _number_to_letters(26)
    'Z'
    >>> _number_to_letters(27)
    'AA'
    >>> _number_to_letters(52)
    'AZ'

    '''
    def n2a(n):
        uc = ascii_uppercase
        d, m = divmod(n, len(uc))
        return n2a(d - 1) + uc[m] if d else uc[m]
    return n2a(int(n) - 1)


def _validate_references_down(dir_path):
    logging.info(f'Validating data_path...')
    with open(dir_path / 'metadata.tsv') as tsv:
        reader = csv.DictReader(tsv, delimiter='\t')
        error_messages = []
        for i, row in enumerate(reader):
            data_path = row['data_path']
            if not (dir_path / data_path).is_dir():
                error_messages.append(
                    f'On row {i+1}, data_path "{data_path}" not a directory')
    # TODO: and also check for unused directories.
    if error_messages:
        raise TableValidationErrors('\n'.join(error_messages))
