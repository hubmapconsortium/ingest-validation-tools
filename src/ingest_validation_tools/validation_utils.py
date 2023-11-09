import json
import logging
from csv import DictReader
from pathlib import Path, PurePath
from typing import Dict, List, Optional, Union

import requests

from ingest_validation_tools.schema_loader import (
    PreflightError,
    SchemaVersion,
    get_table_schema,
    get_other_schema,
    get_directory_schema,
    get_table_schema_version_from_row,
)
from ingest_validation_tools.directory_validator import (
    validate_directory,
    DirectoryValidationErrors,
)
from ingest_validation_tools.table_validator import get_table_errors, ReportType
from ingest_validation_tools.test_validation_utils import (
    compare_mock_with_response,
    mock_response,
)


class TableValidationErrors(Exception):
    pass


def dict_reader_wrapper(path, encoding: str) -> list:
    with open(path, encoding=encoding) as f:
        rows = list(DictReader(f, dialect="excel-tab"))
    return rows


def get_table_schema_version(
    path: Path,
    encoding: str,
    globus_token: str,
    directory_path: Optional[Path] = None,
    offline: bool = False,
) -> SchemaVersion:
    rows = _read_rows(path, encoding)
    assay_type_data = {}
    other_type = get_other_schema_name(rows, str(path))
    # Don't want to send sample/antibody to soft assay endpoint
    if not other_type:
        if not globus_token:
            offline = True
        assay_type_data = get_assaytype_data(
            rows[0],
            globus_token,
            path,
            offline=offline,
        )
        if not assay_type_data:
            raise Exception(
                f"""
                No assay type data found for {path}.
                """
            )
    # TODO: schema_version can be excised once local validation is no longer supported
    if not rows[0].get("metadata_schema_id"):
        version = get_table_schema_version_from_row(str(path), rows[0]).version
    else:
        # TODO: Fix this because we can't force the version to be 2 forever.
        version = "2"
    return SchemaVersion(
        assay_type_data["assaytype"].lower(),
        version,
        directory_path=directory_path,
        path=path,
        rows=rows,
        soft_assay_data=assay_type_data,
    )


def get_other_schema_name(rows: List, path: str) -> Optional[str]:
    other_types = {"organ": "organ_id", "sample": "sample_id"}
    other_type = [key for key, value in other_types.items() if value in rows[0].keys()]
    if len(other_type) == 1:
        return other_type[0]
    elif len(other_type) > 1:
        raise Exception(f"Multiple types found for path {path}. Types: {other_type}")
    else:
        return None


def get_ingest_api_env(env: str) -> str:
    if env in ["dev", "test", "stage"]:
        return f"https://ingest-api.{env}.hubmapconsortium.org/assaytype"
    elif env == "prod":
        return "https://ingest.api.hubmapconsortium.org/assaytype"
    elif env == "local":
        return "http://localhost:5000/assaytype"
    else:
        raise Exception(f"Environment {env} not found!")


def get_assaytype_data(
    row: Dict,
    globus_token: str,
    path: Path,
    env: str = "local",
    offline: bool = False,
) -> Dict:
    if offline:
        return mock_response(path, row)
    url = get_ingest_api_env(env)
    headers = {
        "Authorization": "Bearer " + globus_token,
        "Content-Type": "application/json",
    }
    response = requests.post(url, headers=headers, data=json.dumps(row))
    response.raise_for_status()
    compare_mock_with_response(row, response.json(), path)
    return response.json()


def get_directory_schema_versions(
    tsv_path: str,
    schema_version: SchemaVersion,
    encoding: str,
) -> List:
    parent = Path(tsv_path).parent
    data_paths = [r.get("data_path") for r in _read_rows(tsv_path, encoding)]
    return list(
        set(
            _get_directory_schema_version(parent / path, schema_version=schema_version)
            for path in data_paths
            if path and schema_version
        )
    )


def _read_rows(path, encoding: str):
    try:
        rows = dict_reader_wrapper(path, encoding)
    except UnicodeDecodeError as e:
        raise PreflightError(get_context_of_decode_error(e))
    except IsADirectoryError:
        raise PreflightError(f"Expected a TSV, found a directory at {path}.")
    if not rows:
        raise PreflightError(f"{path} has no data rows.")
    return rows


def _get_directory_schema_version(
    data_path: str,
    schema_version: SchemaVersion,
    is_cedar: bool = False,
) -> str:
    prefix = "dir-schema-v"
    version_hints = [
        path.name for path in (Path(data_path) / "extras").glob(f"{prefix}*")
    ]
    if schema_version.dir_schema_version and not version_hints:
        return schema_version.dir_schema_version
    elif version_hints:
        len_hints = len(version_hints)
        # CEDAR schemas are all v2+; if no hints are provided, default to
        # data directory schema v2
        if len_hints == 0 and is_cedar:
            return "2"
        # For non-CEDAR templates, default to data directory schema v0 if
        # no hints provided
        elif len_hints == 0 and not is_cedar:
            return "0"
        elif len_hints == 1:
            return version_hints[0].replace(prefix, "")
        else:
            raise Exception(f"Expect 0 or 1 hints, not {len_hints}: {version_hints}")
    else:
        raise Exception(
            f"""
            Didn't receive schema_label/version for path {data_path},
            can't find dir schema version.
            """
        )


def get_data_dir_errors(
    schema_version: SchemaVersion,
    data_path: Path,
    is_cedar: bool,
    dataset_ignore_globs: List[str] = [],
) -> Optional[dict]:
    """
    Validate a single data_path.
    Still using _get_directory_schema_version to return the version
    here to accommodate (and privilege) remaining extras dirs in
    local validation
    """
    dir_schema_version = _get_directory_schema_version(
        str(data_path), schema_version=schema_version, is_cedar=is_cedar
    )
    if schema_version.dir_schema_version != dir_schema_version:
        schema_version.dir_schema_version = dir_schema_version
        schema_version.dir_schema = (
            f"{schema_version.schema_name}-v{dir_schema_version}"
        )
    return _get_data_dir_errors_for_version(
        schema_version,
        data_path,
        dataset_ignore_globs,
    )


def _get_data_dir_errors_for_version(
    schema_version: SchemaVersion,
    data_path: Path,
    dataset_ignore_globs: List[str],
) -> Optional[dict]:
    """
    TODO: if we can assume that every SchemaVersion has a dir_schema and
    we can omit the version number, that simplifies this function signature
    to just take a SchemaVersion object as well as simplifying
    validation_utils > get_directory_schema
    """
    schema = get_directory_schema(
        schema_version.schema_name, schema_version=schema_version
    )

    if schema is None:
        return {"Undefined directory schema": schema_version.dir_schema}

    schema_warning_fields = [
        field for field in schema if field in ["deprecated", "draft"]
    ]
    schema_warning = (
        {
            f"{schema_warning_fields[0].title()} directory schema": schema_version.dir_schema
        }
        if schema_warning_fields
        else None
    )

    try:
        validate_directory(
            data_path, schema["files"], dataset_ignore_globs=dataset_ignore_globs
        )
    except DirectoryValidationErrors as e:
        # If there are DirectoryValidationErrors and the schema is deprecated/draft...
        #    schema deprecation/draft status is more important.
        if schema_warning:
            return schema_warning
        errors = {}
        errors[f"{data_path} (as {schema_version.dir_schema})"] = e.errors
        return errors
    except OSError as e:
        # If there are OSErrors and the schema is deprecated/draft...
        #    the OSErrors are more important.
        return {
            f"{data_path} (as {schema_version.dir_schema})": {e.strerror: e.filename}
        }
    if schema_warning:
        return schema_warning

    # No problems!
    return None


def get_context_of_decode_error(e: UnicodeDecodeError) -> str:
    """
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

    """
    buffer = 20
    codec = "latin-1"  # This is not the actual codec of the string!
    before = e.object[max(e.start - buffer, 0) : max(e.start, 0)].decode(codec)  # noqa
    problem = e.object[e.start : e.end].decode(codec)  # noqa
    after = e.object[e.end : min(e.end + buffer, len(e.object))].decode(codec)  # noqa
    in_context = f"{before} [ {problem} ] {after}"
    return f'Invalid {e.encoding} because {e.reason}: "{in_context}"'


def get_other_names():
    return [
        p.stem.split("-v")[0]
        for p in (Path(__file__).parent / "table-schemas/others").iterdir()
    ]


def get_tsv_errors(
    tsv_path: Union[str, Path],
    schema_name: str,
    optional_fields: List[str] = [],
    offline: bool = False,
    encoding: str = "utf-8",
    ignore_deprecation: bool = False,
    report_type: ReportType = ReportType.STR,
) -> Union[Dict[str, str], List[str]]:
    """
    Validate the TSV.

    >>> import tempfile
    >>> from pathlib import Path

    >>> get_tsv_errors('no-such.tsv', 'fake')
    {'File does not exist': 'no-such.tsv'}

    >>> with tempfile.TemporaryDirectory() as dir:
    ...     tsv_path = Path(dir)
    ...     errors = get_tsv_errors(tsv_path, 'fake')
    ...     assert errors['Expected a TSV, but found a directory'] == str(tsv_path)

    # TODO: these are broken due to the addition of paths to error messages
    # >>> with tempfile.TemporaryDirectory() as dir:
    # ...     tsv_path = Path(dir) / 'fake.tsv'
    # ...     tsv_path.write_bytes(b'\\xff')
    # ...     get_tsv_errors(tsv_path, 'fake')
    # 1
    # {'Decode Error': 'Invalid utf-8 because invalid start byte: " [ ÿ ] "'}
    #
    # >>> def test_tsv(content, assay_type='fake'):
    # ...     with tempfile.TemporaryDirectory() as dir:
    # ...         tsv_path = Path(dir) / 'fake.tsv'
    # ...         tsv_path.write_text(content)
    # ...         return get_tsv_errors(tsv_path, assay_type)
    #
    # >>> test = test_tsv('just_a_header_not_enough')
    # >>> print(test, tsv_path)
    # >>> assert test['File has no data rows'] == str(tsv_path)
    #
    # >>> test_tsv('fake_head\\nfake_data')
    # {'No such file or directory': 'fake-v0.yaml'}
    #
    # >>> test_tsv('fake_head\\nfake_data', assay_type='nano')
    # {'Schema version is deprecated': 'nano-v0'}
    #
    # >>> test_tsv('version\\n1', assay_type='nano')
    # {'Schema version is deprecated': 'nano-v1'}
    #
    # >>> test_tsv('version\\n2', assay_type='nano')
    # {'No such file or directory': 'nano-v2.yaml'}
    #
    # >>> test_tsv('version\\n1', assay_type='codex')
    # ['Could not determine delimiter']
    #
    # >>> errors = test_tsv('version\\tfake\\n1\\tfake', assay_type='codex')
    # >>> assert 'Unexpected fields' in errors[0]
    """

    logging.info(f"Validating {schema_name} TSV...")
    if not Path(tsv_path).exists():
        return {"File does not exist": f"{tsv_path}"}

    try:
        rows = dict_reader_wrapper(tsv_path, encoding=encoding)
    except IsADirectoryError:
        return {"Expected a TSV, but found a directory": f"{tsv_path}"}
    except UnicodeDecodeError as e:
        return {"Decode Error": get_context_of_decode_error(e)}

    if not rows:
        return {"File has no data rows": f"{tsv_path}"}

    is_cedar = rows[0].get("metadata_schema_id")

    version = "0"
    # TODO: Fix this because we can't force the version to be 2 forever.
    if is_cedar:
        version = "2"
    elif "version" in rows[0]:
        version = rows[0]["version"]

    if is_cedar:
        from ingest_validation_tools.upload import Upload

        upload = Upload(Path(tsv_path).parent)
        errors = upload.api_validation(Path(tsv_path), report_type)
        schema_version = SchemaVersion(schema_name, version)
        return errors | upload._cedar_url_checks(str(tsv_path), schema_version)

    try:
        schema = get_schema_with_constraints(
            schema_name, version, offline, optional_fields
        )
    except OSError as e:
        return {e.strerror: Path(e.filename).name}

    if schema.get("deprecated") and not ignore_deprecation:
        return {"Schema version is deprecated": f"{schema_name}-v{version}"}

    return get_table_errors(tsv_path, schema, report_type)


def get_schema_with_constraints(
    schema_name: str,
    version: str,
    offline: bool = False,
    optional_fields: List[str] = [],
) -> dict:
    others = get_other_names()
    if schema_name in others:
        schema = get_other_schema(schema_name, version, offline=offline)
    else:
        schema = get_table_schema(
            schema_name, version, offline=offline, optional_fields=optional_fields
        )
    return schema


def print_path(path):
    """
    Attempts to solve issue of YAML dump formatting
    adding ? and breaking keys across multiple lines
    when a path is too long.
    """
    if len(path) > 122:
        new_path = PurePath(path)
        parts = new_path.parts[-3:]
        path = "File .../" + "/".join(str(part) for part in parts)
    return str(path)


def get_json(
    error: str, row: Optional[str] = None, column: Optional[str] = None
) -> Dict[str, Optional[str]]:
    return {
        "column": column,
        "error": error,
        "row": row,
    }
