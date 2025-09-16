import json
import logging
import sys
from csv import DictReader
from pathlib import Path, PurePath
from typing import Optional, Union
from urllib.parse import quote, urljoin

import requests

from ingest_validation_tools.directory_validator import (
    DirectoryValidationErrors,
    validate_directory,
)
from ingest_validation_tools.enums import (
    OTHER_FIELDS_UNIQUE_FIELDS_MAP,
    UNIQUE_FIELDS_MAP,
    CedarSchemaVersionTypes,
    DatasetType,
    EntityTypes,
    OtherTypes,
    Sample,
)
from ingest_validation_tools.local_validation.table_validator import ReportType
from ingest_validation_tools.schema_loader import (
    EntityTypeInfo,
    PreflightError,
    SchemaVersion,
    get_possible_directory_schemas,
)

# TSV Metadata Validator
CEDAR_VALIDATION_URL = "https://api.metadatavalidator.metadatacenter.org/service/validate-tsv"
# Base URL to use for version checking
CEDAR_VERSIONS_URL_BASE = "https://resource.metadatacenter.org/templates/"
# Single template base URL
CEDAR_SINGLE_TEMPLATE_URL_BASE = "https://repo.metadatacenter.org/templates/"


def match_field_in_unique_fields(
    match_fields: list, path: str, dataset=True
) -> Optional[tuple[EntityTypes, str]]:
    match_dict = UNIQUE_FIELDS_MAP
    if not dataset:
        match_dict = OTHER_FIELDS_UNIQUE_FIELDS_MAP
    matches = {}
    for entity_type, unique_fields in match_dict.items():
        match = {
            entity_type: fieldname for fieldname in match_fields if fieldname in unique_fields
        }
        if match:
            matches.update(match)
    if len(matches) > 1:
        raise Exception(
            f"Multiple entity type fields found in {path}: {', '.join([val for (_, val) in matches])}."
        )
    elif len(matches) == 0:
        return None
    return list(matches.items())[0]


class TSVError(Exception):
    def __init__(self, error):
        self.errors = f"{list(error.keys())[0]}: {list(error.values())[0]}"


def dict_reader_wrapper(path, encoding: str) -> list:
    with open(path, encoding=encoding) as f:
        rows = list(DictReader(f, dialect="excel-tab"))
        f.close()
    return rows


def get_schema_version(
    path: Path,
    encoding: str,
    entity_url: str = "",
    ingest_url: str = "",
    globus_token: str = "",
    directory_path: Optional[Path] = None,
) -> SchemaVersion:
    try:
        rows = read_rows(path, encoding)
    except TSVError as e:
        raise PreflightError(e.errors)
    # Don't want to send contrib/organ/sample/antibody to soft assay endpoint
    other_type = get_other_type_schema(rows, str(path), entity_url, globus_token, directory_path)
    if other_type:
        return other_type
    message = []
    if not [field for field in UNIQUE_FIELDS_MAP[DatasetType.DATASET] if field in rows[0].keys()]:
        message.append(
            f"Required dataset field not present in {path}. One of the following is required: {', '.join(sorted(UNIQUE_FIELDS_MAP[DatasetType.DATASET]))}"
        )
        if "channel_id" in rows[0]:
            message.append('Has "channel_id": Antibodies TSV found where metadata TSV expected.')
        elif "orcid_id" in rows[0]:
            message.append('Has "orcid_id": Contributors TSV found where metadata TSV expected.')
    if message:
        raise PreflightError(" ".join([msg for msg in message]))
    assay_type_data = get_assaytype_data(rows[0], ingest_url, globus_token)
    if not assay_type_data:
        message.append(f"No match found in assayclassifier for TSV {path}.")
        if "assay_type" in rows[0]:
            message.append(f'Assay type: {rows[0].get("assay_type")}.')
        elif "dataset_type" in rows[0]:
            message.append(
                f'Dataset type: {rows[0].get("dataset_type")}. Data Curator: check Pipeline Decision Rules to determine correct Assay Type and make sure metadata TSV matches the specification for that type.'
            )
        raise PreflightError(" ".join([msg for msg in message]))
    dataset_type = assay_type_data["assaytype"]
    return SchemaVersion(
        dataset_type,
        directory_path=directory_path,
        path=path,
        rows=rows,
        soft_assay_data=assay_type_data,
        entity_type_info=EntityTypeInfo(DatasetType.DATASET, dataset_type),
    )


def get_other_type_schema(
    rows: list,
    path: str,
    entity_url: str,
    globus_token: str,
    directory_path: Optional[Path] = None,
) -> Optional[SchemaVersion]:
    # Assumes that an entire TSV only represents a single entity_type.
    match_pair = match_field_in_unique_fields(rows[0].keys(), path, dataset=False)
    if match_pair:
        other_type_info = get_other_schema_data(
            rows[0], path, entity_url, globus_token, match_pair
        )
        if other_type_info:
            # Samples are sent as generic "sample" type, subtype is in entity_type_info
            sv = SchemaVersion(
                other_type_info.entity_type.value,
                directory_path=directory_path,
                path=Path(path),
                rows=rows,
                entity_type_info=other_type_info,
            )
            return sv


def get_other_schema_data(
    row: dict,
    path: str,
    entity_url: str,
    globus_token: str,
    entity_field_pair: tuple[EntityTypes, str],
) -> EntityTypeInfo:
    entity_type = entity_field_pair[0]
    unique_field = entity_field_pair[1]
    # Double check this is not a badly-formatted metadata.tsv
    if set(row.keys()).intersection(UNIQUE_FIELDS_MAP[DatasetType.DATASET]):
        raise PreflightError(f"Metadata TSV {path} contains invalid field: {unique_field}")
    if entity_type == OtherTypes.SAMPLE:
        # Sample types require additional data
        return get_entity_info_from_entity_api(entity_url, row[unique_field], globus_token)
    else:
        return EntityTypeInfo(entity_type)


def get_assaytype_data(row: dict, ingest_url: str, globus_token: str) -> dict:
    if not ingest_url:
        ingest_url = "https://ingest.api.hubmapconsortium.org/"
    # The assaytype endpoint checks sample IDs but will not return a verbose error if one is invalid
    if row.get("parent_sample_id"):
        row.pop("parent_sample_id")
    response = requests.post(
        urljoin(ingest_url, "assaytype"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {globus_token}",
        },
        data=json.dumps(row),
    )
    response.raise_for_status()
    return response.json()


def read_rows(path: Path, encoding: str) -> list:
    message = None
    if not Path(path).exists():
        message = {"File does not exist": path}
        raise TSVError(message)
    try:
        rows = dict_reader_wrapper(path, encoding)
        if not rows:
            message = {"File has no data rows": path}
        else:
            return rows
    except IsADirectoryError:
        message = {"Expected a TSV, but found a directory": path}
    except UnicodeDecodeError as e:
        message = {"Decode Error": get_context_of_decode_error(e)}
    raise TSVError(message)


def get_data_dir_errors(
    dir_schema: str,
    root_path: Path,
    data_dir_path: Path,
    dataset_ignore_globs: list[str] = [],
) -> dict[str, Union[dict, str]]:
    """
    Validate a single data_path.
    """
    expected_shared_directories = {"global", "non_global"}
    # Create the most common data_path
    data_paths = [root_path / data_dir_path]

    # Check to see whether the shared upload directories exist
    shared_directories = {
        x for x in root_path.glob("*") if x.is_dir() and x.name in expected_shared_directories
    }

    # Iterate over the set of paths and ensure that the names of those paths
    # matches the set of expected shared directories above
    if {x.name for x in shared_directories} == expected_shared_directories:
        # If they exist create a list of the paths
        data_paths = list(shared_directories)
    # Otherwise, do nothing we can just use the predefined data_path

    possible_schemas = get_possible_directory_schemas(dir_schema)

    if possible_schemas is None:
        return {dir_schema: "No matching directory schemas found."}

    # Collect errors, discard if schema validates against a minor version
    errors = []

    # Make sure possible_schemas is sorted by key (descending) to evaluate highest minor version first
    for schema_name, schema in sorted(possible_schemas.items(), reverse=True):
        schema_warning_fields = [field for field in schema if field in ["deprecated", "draft"]]
        schema_warning = (
            f"{schema_warning_fields[0].title()} directory schema: {schema_name}"
            if schema_warning_fields
            else None
        )

        try:
            validate_directory(
                data_paths, schema["files"], dataset_ignore_globs=dataset_ignore_globs
            )
        except DirectoryValidationErrors as e:
            # If there are DirectoryValidationErrors and the schema is deprecated/draft...
            #    schema deprecation/draft status is more important.
            if schema_warning:
                errors.append({schema_name: schema_warning})
            else:
                errors.append({schema_name: e.errors})
            continue
        except OSError as e:
            # If there are OSErrors and the schema is deprecated/draft...
            #    the OSErrors are more important.
            if isinstance(e, FileNotFoundError):
                raise FileNotFoundError()
            errors.append({schema_name: f"{e.strerror}: {e.filename}"})
            continue
        # Found a schema with no problems!
        # Throw away any found errors.
        return {schema_name: {}}
    # Did not find a schema that validated;
    # return first (highest) schema version errors.
    if errors:
        return errors[0]
    raise Exception(
        f"Unknown error validating directory schema: {[x.as_posix() for x in data_paths]}"
    )


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


def is_schema_latest_version(
    schema_version: str,
    cedar_api_key: str,
    latest_version_name: str = CedarSchemaVersionTypes.IS_LATEST_VERSION.value,
) -> bool:
    """
    Returns true/false if the provided schema version is the latest version.
    Can accept an alternative `latest_version_name` that will check against a specific key. These can be:
        isLatestVersion,
        isLatestPublishedVersion,
        isLatestDraftVersion
    This function defaults to checking against `isLatestVersion`
    """
    try:
        latest_version_name = CedarSchemaVersionTypes(latest_version_name)
    except KeyError as ke:
        message = {f"Invalid latest_version_name {latest_version_name}": ke}
        raise TSVError(message)

    latest_version = get_latest_schema_version(schema_version, cedar_api_key, latest_version_name)
    return schema_version == latest_version


def get_latest_schema_version(
    schema_version: str,
    cedar_api_key: str,
    latest_version_name: CedarSchemaVersionTypes,
) -> str:
    latest_schema_version = ""
    try:
        schema_details = get_schema_details(schema_version, cedar_api_key)
        if "resources" not in schema_details:
            message = {
                f"Error occurred while gathering schemas for schema {schema_version}": f"{schema_details['errorMessage']}"
            }
            raise TSVError(message)
        for schema in schema_details["resources"]:
            if schema[latest_version_name.value]:
                latest_schema_version = schema["@id"].removeprefix(CEDAR_SINGLE_TEMPLATE_URL_BASE)
            break
        return latest_schema_version

    except TSVError as te:
        raise te
    except Exception as e:
        logging.exception(f"Exception while gathering schemas for schema {schema_version}. {e}")
        message = {f"Exception while gathering schemas for schema {schema_version}": e}
        raise TSVError(message)


def get_schema_details(schema_version: str, cedar_api_key: str) -> dict:
    logging.debug(f"======get_schema_details: {schema_version}======")
    encoded_template_url = quote(f"{CEDAR_SINGLE_TEMPLATE_URL_BASE}{schema_version}", safe="")
    response = requests.get(
        url=urljoin(CEDAR_VERSIONS_URL_BASE, f"{encoded_template_url}/versions"),
        headers={
            "Accept": "application/json",
            "Authorization": f"apiKey {cedar_api_key}",
        },
    )
    return response.json()


def get_tsv_errors(
    tsv_path: Union[str, Path],
    schema_name: str,
    no_url_checks: bool = False,
    ignore_deprecation: bool = False,
    report_type: ReportType = ReportType.STR,
    globus_token: str = "",
    app_context: dict = {},
) -> list:
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

    # TODO: refactor into TSV class
    upload = Upload(
        Path(tsv_path).parent,
        tsv_paths=[Path(tsv_path)],
        globus_token=globus_token,
        offline_only=no_url_checks,
        ignore_deprecation=ignore_deprecation,
        app_context=app_context,
        report_type=report_type,
    )
    # Return preflight errors to prevent uncaught exceptions downstream
    if upload.errors.preflight:
        return upload.errors.tsv_only_errors_by_path(str(tsv_path), report_type=report_type)
    if schema_name in OtherTypes.with_sample_subtypes():
        try:
            schema = upload.get_schema_from_path(Path(tsv_path))
        except Exception as e:
            if upload.errors:
                upload.errors.upload_metadata[tsv_path].append(str(e))
        else:
            upload.validate_metadata(tsv_paths={schema.path: schema})
    else:
        upload.validate_metadata()
    return upload.errors.tsv_only_errors_by_path(str(tsv_path), report_type=report_type)


def cedar_validation_call(tsv_path: Union[str, Path]) -> requests.models.Response:
    with open(tsv_path, "rb") as f:
        file = {"input_file": f}
        headers = {
            "content_type": "multipart/form-data",
        }
        try:
            response = requests.post(
                CEDAR_VALIDATION_URL,
                headers=headers,
                files=file,
            )
            logging.info(f"Response: {response.json()}")
        except Exception as e:
            raise Exception(
                f"Spreadsheet Validator API request for {tsv_path} failed! Exception: {e}"
            )
    return response


def get_entity_api_data(
    entity_api_url: str,
    entity_id: str,
    globus_token: str,
    headers: Optional[dict] = None,
) -> requests.Response:
    if not globus_token:
        raise Exception("No token received to check URL fields against Entity API.")
    if not headers:
        headers = {}
    headers["Authorization"] = f"Bearer {globus_token}"
    url = f"{urljoin(entity_api_url, 'entities')}/{entity_id}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response


def get_entity_info_from_entity_api(
    entity_url: str,
    entity_id: str,
    globus_token: str,
    headers: Optional[dict] = None,
) -> EntityTypeInfo:
    """
    Make an entity-api call and from the response, get
    entity_type, subtype data (e.g. "block" for sample), and
    any sub_type_val values (currently just organ codes, e.g. "BD")
    and return as a dict in the format expected by the constraints endpoint.
    """
    response = get_entity_api_data(entity_url, entity_id, globus_token, headers)
    entity_type, entity_sub_type, entity_sub_type_val = get_entity_type_vals(response.json())
    return EntityTypeInfo(entity_type, entity_sub_type, entity_sub_type_val)


def get_entity_type_vals(response: dict) -> tuple:
    raw_entity_type = response.get("entity_type", "").lower()
    entity_sub_type = None
    entity_sub_type_val = None
    if raw_entity_type == DatasetType.DATASET:
        entity_type = DatasetType.DATASET
        entity_sub_type = response.get("dataset_type", "")
    else:
        entity_type = OtherTypes.get_enum_from_val(raw_entity_type)
        if entity_type == OtherTypes.SAMPLE:
            entity_sub_type = response.get("sample_category", "").lower()
            if entity_sub_type == Sample.ORGAN:
                entity_sub_type_val = response.get("organ", "").lower()
    return entity_type, entity_sub_type, entity_sub_type_val


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
) -> dict[str, Optional[str]]:
    return {
        "column": column,
        "error": error,
        "row": row,
    }


def get_message(
    error: dict[str, str], report_type: ReportType = ReportType.STR
) -> Union[str, dict]:
    """
    >>> print(
    ...     get_message(
    ...         {
    ...             'errorType': 'notStandardTerm',
    ...             'column': 'stain_name',
    ...             'row': 1,
    ...             'repairSuggestion': 'H&E',
    ...             'value': 'H& E'
    ...         },
    ...     )
    ... )
    On row 3, column "stain_name", value "H& E" fails because of error "notStandardTerm". Example: H&E
    """  # noqa: E501

    example = error.get("repairSuggestion", "")
    error_text = error.get("error_text", "")

    return_str = report_type is ReportType.STR
    if "errorType" in error and "column" in error and "row" in error and "value" in error:
        assert type(error["row"]) is int
        error["row"] = error["row"] + 2
        # This may need readability improvements
        msg = (
            f'value "{error["value"]}" fails because of error "{error["errorType"]}"'
            f'{f": {error_text}" if error_text else error_text}'
            f'{f". Example: {example}" if example else example}'
        )
        full_msg = f'On row {error["row"]}, column "{error["column"]}", {msg}'
        return full_msg if return_str else get_json(msg, error["row"], error["column"])
    return error


def find_empty_tsv_columns(tsv_path: Path) -> list[str]:
    empty = []
    with open(tsv_path) as f:
        try:
            dr = DictReader(f, dialect="excel-tab")
            assert dr.fieldnames
        except Exception:
            # Errors in TSV should have been caught already, but just to be safe.
            return [f"Error opening {tsv_path}."]
        for index, column in enumerate(dr.fieldnames):
            if column in ["", " "]:
                empty.append(str(index))
        f.close()
    return empty


class add_path:
    """
    Add an element to sys.path using a context.
    Thanks to Eugene Yarmash https://stackoverflow.com/a/39855753
    """

    def __init__(self, path):
        self.path = path

    def __enter__(self):
        sys.path.insert(0, self.path)

    def __exit__(self, exc_type, exc_value, traceback):
        del exc_type, exc_value, traceback
        try:
            sys.path.remove(self.path)
        except ValueError:
            pass
