import logging
from csv import DictReader
from pathlib import Path

from ingest_validation_tools.schema_loader import (
    get_table_schema, get_other_schema,
    get_directory_schema)
from ingest_validation_tools.directory_validator import (
    validate_directory, DirectoryValidationErrors)
from ingest_validation_tools.table_validator import (
    get_table_errors)


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

    errors = {}
    if internal_errors:
        errors['Internal'] = internal_errors

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
    return get_table_errors(tsv_path, schema)
