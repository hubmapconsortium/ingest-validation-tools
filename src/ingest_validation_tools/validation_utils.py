import logging
import re
from string import ascii_uppercase
from csv import DictReader
from pathlib import Path

import requests
from goodtables import validate as validate_table

from ingest_validation_tools.schema_loader import (
    get_table_schema, get_other_schema,
    get_directory_schema)
from ingest_validation_tools.directory_validator import (
    validate_directory, DirectoryValidationErrors)


class TableValidationErrors(Exception):
    pass


def dict_reader_wrapper(path, encoding):
    with open(path, encoding=encoding) as f:
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


status_of_id: dict = {
    'orcid_id': {},
    'rr_id': {},
    'uniprot_accession_number': {}
}


def get_context_of_decode_error(e):
    '''
    >>> try:
    ...   b'\\xFF'.decode('ascii')
    ... except UnicodeDecodeError as e:
    ...   print(get_context_of_decode_error(e))
    Invalid ascii because ordinal not in range(128): " [ ÿ ] "

    >>> try:
    ...   b'01234\\xFF6789'.decode('ascii')
    ... except UnicodeDecodeError as e:
    ...   print(get_context_of_decode_error(e))
    Invalid ascii because ordinal not in range(128): "01234 [ ÿ ] 6789"

    >>> try:
    ...   (b'a string longer than twenty characters\\xFFa string '
    ...    b'longer than twenty characters').decode('utf-8')
    ... except UnicodeDecodeError as e:
    ...   print(get_context_of_decode_error(e))
    Invalid utf-8 because invalid start byte: "an twenty characters [ ÿ ] a string longer than"

    '''
    buffer = 20
    codec = 'latin-1'  # This is not the actual codec of the string!
    before = e.object[max(e.start - buffer, 0):max(e.start, 0)].decode(codec)
    problem = e.object[e.start:e.end].decode(codec)
    after = e.object[e.end:min(e.end + buffer, len(e.object))].decode(codec)
    in_context = f'{before} [ {problem} ] {after}'
    return f'Invalid {e.encoding} because {e.reason}: "{in_context}"'


def _get_in_ex_errors(path, type_name, field_url_pairs, encoding=None, offline=None):
    if not path.exists():
        return 'File does not exist'
    try:
        rows = dict_reader_wrapper(path, encoding)
    except UnicodeDecodeError as e:
        return get_context_of_decode_error(e)
    if not rows:
        return 'File has no data rows.'

    internal_errors = get_tsv_errors(path, type_name)
    external_errors = {}
    if not offline:
        for field, url_base in field_url_pairs:
            status_cache = status_of_id[field]
            for i, row in enumerate(rows):
                row_number = f'row {i+2}'
                id_to_check = row[field]
                if id_to_check not in status_cache:
                    response = requests.get(f'{url_base}{id_to_check}')
                    status_cache[id_to_check] = response.status_code
                if status_cache[id_to_check] != requests.codes.ok:
                    label = f'{row_number}, {field} {id_to_check}'
                    external_errors[label] = status_cache[id_to_check]

    errors = {}
    if internal_errors:
        errors['Internal'] = internal_errors
    if external_errors:
        errors['External'] = external_errors

    return errors


def get_contributors_errors(contributors_path, encoding=None, offline=None):
    '''
    Validate a single contributors file.
    '''
    return _get_in_ex_errors(
        contributors_path, 'contributors', [
            ('orcid_id', 'https://orcid.org/')
        ],
        encoding=encoding,
        offline=offline
    )


def get_antibodies_errors(antibodies_path, encoding=None, offline=None):
    '''
    Validate a single antibodies file.
    '''
    return _get_in_ex_errors(
        antibodies_path, 'antibodies', [
            ('rr_id', 'https://scicrunch.org/resolver/RRID:'),
            ('uniprot_accession_number', 'https://www.uniprot.org/uniprot/')
        ],
        encoding=encoding,
        offline=offline
    )


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
