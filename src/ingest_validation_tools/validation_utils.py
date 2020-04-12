from pathlib import Path
import logging
import re
from string import ascii_uppercase

from yaml import safe_load as load_yaml
from goodtables import validate as validate_table

from ingest_validation_tools.table_schema_loader import get_schema
from ingest_validation_tools.directory_validator.validator import \
    validate as validate_directory
from ingest_validation_tools.directory_validator.errors import \
    DirectoryValidationErrors


class TableValidationErrors(Exception):
    pass


def get_data_dir_errors(type, data_path):
    '''
    Validate a single data_path.
    '''
    schema_path = (
        Path(__file__).parent /
        'directory-schemas' /
        f'{type}.yaml')
    schema = load_yaml(open(schema_path).read())
    try:
        validate_directory(data_path, schema)
    except DirectoryValidationErrors as e:
        return e.object_errors
    except OSError as e:
        return {
            e.strerror:
                e.filename
        }


def get_metadata_tsv_errors(metadata_path, type):
    '''
    Validate the metadata.tsv.
    '''
    logging.info(f'Validating {type} metadata.tsv...')
    try:
        schema = get_schema(type)
    except OSError as e:
        return {
            e.strerror:
                Path(e.filename).name
        }
    report = validate_table(metadata_path, schema=schema,
                            skip_checks=['blank-row'])
    error_messages = report['warnings']
    if 'tables' in report:
        for table in report['tables']:
            error_messages += [
                _column_number_to_letters(e['message'])
                for e in table['errors']
            ]
    return error_messages


def _column_number_to_letters(message):
    '''
    >>> _column_number_to_letters('Column 209 and column 141493 are funny.')
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
