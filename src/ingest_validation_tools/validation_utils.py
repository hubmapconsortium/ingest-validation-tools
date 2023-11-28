import json
import logging
from csv import DictReader
from pathlib import Path, PurePath
from typing import Dict, List, Optional, Union

import requests

from ingest_validation_tools.schema_loader import (
    PreflightError,
    SchemaVersion,
    get_directory_schema,
)
from ingest_validation_tools.directory_validator import (
    validate_directory,
    DirectoryValidationErrors,
)
from ingest_validation_tools.table_validator import ReportType
from ingest_validation_tools.test_validation_utils import (
    compare_mock_with_response,
    mock_response,
)


class TSVError(Exception):
    def __init__(self, error):
        self.errors = f"{list(error.keys())[0]}: {list(error.values())[0]}"


def dict_reader_wrapper(path, encoding: str) -> list:
    with open(path, encoding=encoding) as f:
        rows = list(DictReader(f, dialect="excel-tab"))
    return rows


def get_schema_version(
    path: Path,
    encoding: str,
    globus_token: str,
    directory_path: Optional[Path] = None,
    offline: bool = False,
) -> SchemaVersion:
    try:
        rows = read_rows(path, encoding)
    except TSVError as e:
        raise PreflightError(e.errors)
    # Don't want to send contrib/organ/sample/antibody to soft assay endpoint
    if "dataset_type" not in rows[0] or "assay_type" not in rows[0]:
        other_type = get_other_schema_name(str(path))
        sv = SchemaVersion(
            other_type,
            directory_path=directory_path,
            path=path,
            rows=rows,
        )
        return sv
    assay_type_data = get_assaytype_data(
        rows[0],
        globus_token,
        path,
        offline=offline,
    )
    if not assay_type_data:
        message = get_assaytype_error(rows[0], str(path))
        raise PreflightError(message)
    return SchemaVersion(
        assay_type_data["assaytype"].lower(),
        directory_path=directory_path,
        path=path,
        rows=rows,
        soft_assay_data=assay_type_data,
    )


def get_other_schema_name(path: str) -> str:
    response = metadatavalidator_api_call(path)
    if response.status_code != 200:
        raise PreflightError(
            f"""
            Error retrieving schema info for {path}:
            API returned {response.status_code}.
            Response: {json.dumps(response.json(), indent=2)}
            """
        )
    template_name = response.json().get("schema", {}).get("name")
    # TODO: are these the canonical names? Should these be in the assayclassifier?
    # CEDAR Metadata Center template name : canonical name
    name_map = {
        "sample block": "sample-block",
        "sample suspension": "sample-suspension",
        "sample section": "sample-section",
        "antibodies": "antibodies",
        "contributor": "contributors",
        "organ": "organ",
    }
    if template_name.lower() in name_map.keys():
        return name_map[template_name]
    else:
        raise PreflightError(
            f"Error retrieving schema info for {path}. Invalid template name: {template_name}."
        )


def get_assaytype_error(row: dict, path: str) -> str:
    message = f"No assay data retrieved for {path}."
    dataset_type = (
        row.get("dataset_type") if row.get("dataset_type") else row.get("assay_type")
    )
    if dataset_type:
        message += f" Datset type: {dataset_type}."
    else:
        message += ' Does not contain "assay_type" or "dataset_type".'
    other_fields = [
        "antibody_name",
        "antibody_rrid",
        "channel_id",
        "orcid",
        "orcid_id",
        "organ_id",
        "sample_id",
    ]
    found_fields = [field for field in other_fields if field in row]
    if found_fields:
        message += f" Found invalid field(s) for metadata TSV: {found_fields}"
    message += f' Column headers in TSV: {", ".join(row.keys())}'
    return message


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
    env: str = "dev",
    offline: bool = False,
) -> Dict:
    if "version" in row.keys():
        row["version"] = int(row["version"])
    if offline or not globus_token:
        # TODO: separate testing path from live code
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


def read_rows(path: Path, encoding: str) -> List:
    message = None
    if not Path(path).exists():
        message = {"File does not exist": f"{path}"}
        raise TSVError(message)
    try:
        rows = dict_reader_wrapper(path, encoding)
        if not rows:
            message = {"File has no data rows": f"{path}"}
        else:
            return rows
    except IsADirectoryError:
        message = {"Expected a TSV, but found a directory": f"{path}"}
    except UnicodeDecodeError as e:
        message = {"Decode Error": get_context_of_decode_error(e)}
    raise TSVError(message)


def get_data_dir_errors(
    dir_schema: str,
    data_path: Path,
    dataset_ignore_globs: List[str] = [],
) -> Optional[dict]:
    """
    Validate a single data_path.
    """
    schema = get_directory_schema(dir_schema=dir_schema)

    if schema is None:
        return {"Undefined directory schema": dir_schema}

    schema_warning_fields = [
        field for field in schema if field in ["deprecated", "draft"]
    ]
    schema_warning = (
        {f"{schema_warning_fields[0].title()} directory schema": dir_schema}
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
        errors[f"{data_path} (as {dir_schema})"] = e.errors
        return errors
    except OSError as e:
        # If there are OSErrors and the schema is deprecated/draft...
        #    the OSErrors are more important.
        return {f"{data_path} (as {dir_schema})": {e.strerror: e.filename}}
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


def metadatavalidator_api_call(tsv_path: Union[str, Path]) -> requests.models.Response:
    file = {"input_file": open(tsv_path, "rb")}
    headers = {"content_type": "multipart/form-data"}
    try:
        response = requests.post(
            "https://api.metadatavalidator.metadatacenter.org/service/validate-tsv",
            headers=headers,
            files=file,
        )
    except Exception as e:
        raise Exception(f"CEDAR API request for {tsv_path} failed! Exception: {e}")
    return response


def get_tsv_errors(
    tsv_path: Union[str, Path],
    schema_name: str,
    optional_fields: List[str] = [],
    offline: bool = False,
    ignore_deprecation: bool = False,
    report_type: ReportType = ReportType.STR,
    globus_token: str = "",
) -> Dict[str, str]:
    """
    Validate the TSV.

    >>> import tempfile
    >>> from pathlib import Path

    # >>> get_tsv_errors('no-such.tsv', 'fake')
    # {'TSV Errors': {'File does not exist': 'no-such.tsv'}}
    #
    # >>> with tempfile.TemporaryDirectory() as dir:
    # ...     tsv_path = Path(dir)
    # ...     errors = get_tsv_errors(tsv_path, 'fake')
    # ...     assert errors['Expected a TSV, but found a directory'] == str(tsv_path)
    #
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
    from ingest_validation_tools.upload import Upload

    logging.info(f"Validating {schema_name} TSV...")

    # TODO: this is weird, because we're creating an upload for a single file...maybe subclass?
    upload = Upload(
        Path(tsv_path).parent,
        tsv_paths=[Path(tsv_path)],
        optional_fields=optional_fields,
        globus_token=globus_token,
        offline=offline,
        ignore_deprecation=ignore_deprecation,
    )
    errors = upload.validation_routine(report_type)
    return errors


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
