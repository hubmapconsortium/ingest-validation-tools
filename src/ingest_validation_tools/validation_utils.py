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
from ingest_validation_tools.schema_loader import (
    get_schema_version_from_row, PreflightError
)


class TableValidationErrors(Exception):
    pass


def dict_reader_wrapper(path, encoding):
    with open(path, encoding=encoding) as f:
        rows = list(DictReader(f, dialect='excel-tab'))
    return rows


def get_schema_version(path, encoding):
    try:
        rows = dict_reader_wrapper(path, encoding)
    except UnicodeDecodeError as e:
        raise PreflightError(get_context_of_decode_error(e))
    except IsADirectoryError:
        raise PreflightError(f'Expected a TSV, found a directory at {path}.')
    if not rows:
        raise PreflightError(f'{path} has no data rows.')
    return get_schema_version_from_row(path, rows[0])


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


def get_tsv_errors(
        tsv_path, schema_name, optional_fields=[],
        offline=None, encoding=None, ignore_deprecation=False):
    '''
    Validate the TSV.

    >>> import tempfile
    >>> from pathlib import Path

    >>> get_tsv_errors('no-such.tsv', 'fake')
    'File does not exist'

    >>> with tempfile.TemporaryDirectory() as dir:
    ...     tsv_path = Path(dir)
    ...     get_tsv_errors(tsv_path, 'fake')
    'Expected a TSV, but found a directory'

    >>> with tempfile.TemporaryDirectory() as dir:
    ...     tsv_path = Path(dir) / 'fake.tsv'
    ...     tsv_path.write_bytes(b'\\xff')
    ...     get_tsv_errors(tsv_path, 'fake')
    1
    'Invalid utf-8 because invalid start byte: " [ ÿ ] "'

    >>> def test_tsv(content, assay_type='fake'):
    ...     with tempfile.TemporaryDirectory() as dir:
    ...         tsv_path = Path(dir) / 'fake.tsv'
    ...         tsv_path.write_text(content)
    ...         return get_tsv_errors(tsv_path, assay_type)

    >>> test_tsv('just_a_header_not_enough')
    'File has no data rows.'

    >>> test_tsv('fake_head\\nfake_data')
    {'No such file or directory': 'fake-v0.yaml'}

    >>> test_tsv('fake_head\\nfake_data', assay_type='nano')
    {'Schema version is deprecated': 'nano-v0'}

    >>> test_tsv('version\\n1', assay_type='nano')
    {'Schema version is deprecated': 'nano-v1'}

    >>> test_tsv('version\\n2', assay_type='nano')
    {'No such file or directory': 'nano-v2.yaml'}

    >>> test_tsv('version\\n1', assay_type='codex')
    ['Could not determine delimiter']

    >>> errors = test_tsv('version\\tfake\\n1\\tfake', assay_type='codex')
    >>> assert 'Unexpected fields' in errors[0]
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
    try:
        others = [
            p.stem.split('-v')[0] for p in
            (Path(__file__).parent / 'table-schemas/others').iterdir()
        ]
        if schema_name in others:
            schema = get_other_schema(schema_name, version, offline=offline)
        else:
            schema = get_table_schema(schema_name, version, offline=offline,
                                      optional_fields=optional_fields)
    except OSError as e:
        return {e.strerror: Path(e.filename).name}

    if schema.get('deprecated') and not ignore_deprecation:
        return {'Schema version is deprecated': f'{schema_name}-v{version}'}

    return get_table_errors(tsv_path, schema)
