import logging
from csv import DictReader
from pathlib import Path
from json import dumps

from ingest_validation_tools.schema_loader import (
    get_table_schema, get_other_schema,
    get_directory_schema, get_all_directory_schema_versions)
from ingest_validation_tools.directory_validator import (
    validate_directory, DirectoryValidationErrors)
from ingest_validation_tools.table_validator import (
    get_table_errors)
from ingest_validation_tools.schema_loader import (
    get_table_schema_version_from_row, PreflightError
)


class TableValidationErrors(Exception):
    pass


def dict_reader_wrapper(path, encoding):
    with open(path, encoding=encoding) as f:
        rows = list(DictReader(f, dialect='excel-tab'))
    return rows


def get_table_schema_version(path, encoding):
    try:
        rows = dict_reader_wrapper(path, encoding)
    except UnicodeDecodeError as e:
        raise PreflightError(get_context_of_decode_error(e))
    except IsADirectoryError:
        raise PreflightError(f'Expected a TSV, found a directory at {path}.')
    if not rows:
        raise PreflightError(f'{path} has no data rows.')
    return get_table_schema_version_from_row(path, rows[0])


def _get_best_directory_schema_version(schema_name, data_path, dataset_ignore_globs):
    '''
    Read all schemas, and return the one with the fewest errors.
    (Having an explicit indication of the version of the submission was proposed and rejected.)
    '''
    # Get all directory schemas:
    all_directory_schema_versions = get_all_directory_schema_versions(schema_name)

    # Validate with each:
    all_directory_schemas_errors = [
        (directory_schema_version, _get_data_dir_errors_for_version(
            schema_name, data_path, dataset_ignore_globs, directory_schema_version.version))
        for directory_schema_version in all_directory_schema_versions
    ]

    # Sort for simpler errors at the top:
    all_directory_schemas_errors.sort(key=_get_ugliness)

    # Return the best:
    return all_directory_schemas_errors[0][0]


def _get_ugliness(schema_error):
    '''
    Quantify the ugliness of errors:
    Assume that the least ugly error corresponds to the best schema to validate against.

    >>> good = ({}, None)
    >>> bad = ({}, {'something': 'bad'})
    >>> worse = ({}, {'something': ['worse']})
    >>> worst = ({}, 'Deprecated')
    >>> assert _get_ugliness(good) < _get_ugliness(bad)
    >>> assert _get_ugliness(bad) < _get_ugliness(worse)
    >>> assert _get_ugliness(worse) < _get_ugliness(worst)
    '''
    (_schema, error) = schema_error
    if error is None:
        return 0
    as_json = dumps(schema_error, indent=0)
    if 'Deprecated' in as_json:
        # TODO: Improve this logic.
        return 999
    return len(as_json.split('\n'))


def get_data_dir_errors(schema_name, data_path, dataset_ignore_globs=[]):
    '''
    Validate a single data_path.
    '''
    directory_schema_version = _get_best_directory_schema_version(
        schema_name, data_path, dataset_ignore_globs).version
    return _get_data_dir_errors_for_version(
        schema_name, data_path, dataset_ignore_globs, directory_schema_version)


def _get_data_dir_errors_for_version(
        schema_name, data_path, dataset_ignore_globs, directory_schema_version):
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
