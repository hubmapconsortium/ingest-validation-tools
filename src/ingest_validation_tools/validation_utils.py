import logging
import re
from string import ascii_uppercase
from csv import DictReader
from pathlib import Path

from goodtables import validate as validate_table

from ingest_validation_tools.schema_loader import (
    get_table_schema, get_other_schema,
    get_directory_schema)
from ingest_validation_tools.directory_validator import (
    validate_directory, DirectoryValidationErrors)


class TableValidationErrors(Exception):
    pass


def dict_reader_wrapper(path):
    with open(path, encoding='latin-1') as f:
        rows = list(DictReader(f, dialect='excel-tab'))
    return rows


def get_data_dir_errors(type, data_path, dataset_ignore_globs=[]):
    '''
    Validate a single data_path.
    '''
    schema = get_directory_schema(type)
    try:
        validate_directory(
            data_path, schema, dataset_ignore_globs=dataset_ignore_globs)
    except DirectoryValidationErrors as e:
        return e.errors
    except OSError as e:
        return {e.strerror: e.filename}


def get_contributors_errors(contributors_path):
    '''
    Validate a single contributors file.
    '''
    errors = {}
    internal_errors = get_tsv_errors(contributors_path, 'contributors')
    if internal_errors:
        errors['Contributors internal'] = internal_errors
    # TODO: External
    return internal_errors


def get_antibodies_errors(antibodies_path):
    '''
    Validate a single antibodies file.
    '''
    errors = {}
    internal_errors = get_tsv_errors(antibodies_path, 'antibodies')
    if internal_errors:
        errors['Antibodies internal'] = internal_errors
    # TODO: External
    return internal_errors


def get_tsv_errors(tsv_path, type, optional_fields=[]):
    '''
    Validate the TSV.
    '''
    logging.info(f'Validating {type} TSV...')
    if type is None:
        return f'TSV has no assay_type.'
    try:
        if type in ['contributors', 'antibodies', 'sample']:
            schema = get_other_schema(type)
        else:
            schema = get_table_schema(type, optional_fields=optional_fields)
    except OSError as e:
        return {e.strerror: Path(e.filename).name}
    report = validate_table(tsv_path, schema=schema,
                            format='csv', delimiter='\t',
                            skip_checks=['blank-row'])
    error_messages = report['warnings']
    if 'tables' in report:
        for table in report['tables']:
            error_messages += [
                column_number_to_letters(e['message'])
                for e in table['errors']
            ]
    return error_messages


def column_number_to_letters(message):
    '''
    >>> column_number_to_letters('Column 209 and column 141493 are funny.')
    'Column 209 ("HA") and column 141493 ("HAHA") are funny.'

    '''
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
