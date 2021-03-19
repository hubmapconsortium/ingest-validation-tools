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


def get_data_dir_errors(schema_name, data_path, dataset_ignore_globs=[]):
    '''
    Validate a single data_path.
    '''
    schema = get_directory_schema(schema_name)
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


def get_tsv_errors(tsv_path, schema_name, optional_fields=[], offline=None, encoding=None):
    '''
    Validate the TSV.
    '''
    logging.info(f'Validating {schema_name} TSV...')
    if not Path(tsv_path).exists():
        return 'File does not exist'

    try:
        rows = dict_reader_wrapper(tsv_path, encoding=encoding)
    except IsADirectoryError:
        return 'Expected a TSV, but found a directory'
    except UnicodeDecodeError as e:
        return get_context_of_decode_error(e)

    if not rows:
        return 'File has no data rows.'

    version = rows[0]['version'] if 'version' in rows[0] else '0'
    source_project = rows[0]['source_project'] if 'source_project' in rows[0] else None
    try:
        others = [
            p.stem.split('-v')[0] for p in
            (Path(__file__).parent / 'table-schemas/others').iterdir()
        ]
        if schema_name in others:
            schema = get_other_schema(schema_name, version, source_project=source_project,
                                      offline=offline)
        else:
            schema = get_table_schema(schema_name, version, source_project=source_project,
                                      offline=offline, optional_fields=optional_fields)
    except OSError as e:
        return {e.strerror: Path(e.filename).name}
    return get_table_errors(tsv_path, schema)
