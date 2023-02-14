import logging
from csv import DictReader
from pathlib import Path
from typing import List, Optional

from ingest_validation_tools.schema_loader import (
    SchemaVersion, get_table_schema, get_other_schema,
    get_directory_schema)
from ingest_validation_tools.directory_validator import (
    validate_directory, DirectoryValidationErrors)
from ingest_validation_tools.table_validator import (
    get_table_errors, ReportType)
from ingest_validation_tools.schema_loader import (
    get_table_schema_version_from_row, PreflightError
)


class TableValidationErrors(Exception):
    pass


def dict_reader_wrapper(path, encoding: str) -> list:
    with open(path, encoding=encoding) as f:
        rows = list(DictReader(f, dialect='excel-tab'))
    return rows


def get_table_schema_version(path, encoding: str) -> SchemaVersion:
    rows = _read_rows(path, encoding)
    return get_table_schema_version_from_row(path, rows[0])


def get_directory_schema_versions(tsv_path, encoding: str) -> list:
    parent = Path(tsv_path).parent
    data_paths = [r.get('data_path') for r in _read_rows(tsv_path, encoding)]
    return list(set(_get_directory_schema_version(parent / path) for path in data_paths if path))


def _read_rows(path, encoding: str):
    try:
        rows = dict_reader_wrapper(path, encoding)
    except UnicodeDecodeError as e:
        raise PreflightError(get_context_of_decode_error(e))
    except IsADirectoryError:
        raise PreflightError(f'Expected a TSV, found a directory at {path}.')
    if not rows:
        raise PreflightError(f'{path} has no data rows.')
    return rows


def _get_directory_schema_version(data_path) -> str:
    prefix = 'dir-schema-v'
    version_hints = [path.name for path in (Path(data_path) / 'extras').glob(f'{prefix}*')]
    len_hints = len(version_hints)
    if len_hints == 0:
        return '0'
    elif len_hints == 1:
        return version_hints[0].replace(prefix, '')
    else:
        raise Exception(f'Expect 0 or 1 hints, not {len_hints}: {version_hints}')


def get_data_dir_errors(schema_name: str, data_path: Path,
                        dataset_ignore_globs: List[str] = []) -> Optional[dict]:
    '''
    Validate a single data_path.
    '''
    directory_schema_version = _get_directory_schema_version(data_path)
    return _get_data_dir_errors_for_version(
        schema_name, data_path, dataset_ignore_globs, directory_schema_version)


def _get_data_dir_errors_for_version(
        schema_name: str,
        data_path: Path,
        dataset_ignore_globs: List[str],
        directory_schema_version: str
) -> Optional[dict]:
    schema = get_directory_schema(schema_name, directory_schema_version)
    schema_label = f'{schema_name}-v{directory_schema_version}'

    if schema is None:
        return {'Undefined directory schema': schema_label}

    schema_warning = {'Deprecated directory schema': schema_label} \
        if schema.get('deprecated', False) else None

    try:
        validate_directory(
            data_path, schema['files'], dataset_ignore_globs=dataset_ignore_globs)
    except DirectoryValidationErrors as e:
        # If there are DirectoryValidationErrors and the schema is deprecated...
        #    schema deprecation is more important.
        if schema_warning:
            return schema_warning
        return e.errors
    except OSError as e:
        # If there are OSErrors and the schema is deprecated...
        #    the OSErrors are more important.
        return {e.strerror: e.filename}
    if schema_warning:
        return schema_warning

    # No problems!
    return None


def get_context_of_decode_error(e: UnicodeDecodeError) -> str:
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
        tsv_path: str, schema_name: str, optional_fields: List[str] = [],
        offline=None, encoding: str = 'utf-8', ignore_deprecation: bool = False,
        report_type: ReportType = ReportType.STR):
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

    return get_table_errors(tsv_path, schema, report_type)
