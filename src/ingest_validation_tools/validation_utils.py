from __future__ import annotations

import json
import logging
import sys
from collections import defaultdict
from csv import DictReader
from dataclasses import dataclass
from pathlib import Path, PurePath
from typing import TYPE_CHECKING
from urllib.parse import quote, urlencode, urljoin

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
    PreflightError,
    get_possible_directory_schemas,
)
from ingest_validation_tools.schemas import create_schema_for_entity_type

if TYPE_CHECKING:
    from ingest_validation_tools.schemas import Schema

# TSV Metadata Validator
CEDAR_VALIDATION_URL = "https://api.metadatavalidator.metadatacenter.org/service/validate-tsv"
# Base URL to use for version checking
CEDAR_VERSIONS_URL_BASE = "https://resource.metadatacenter.org/templates/"
# Single template base URL
CEDAR_SINGLE_TEMPLATE_URL_BASE = "https://repo.metadatacenter.org/templates/"


def match_field_in_unique_fields(
    match_fields: list, path: str, dataset=True
) -> tuple[EntityTypes, str] | None:
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
    def __init__(self, error: str):
        self.errors = error


def dict_reader_wrapper(path, encoding: str) -> list:
    with open(path, encoding=encoding) as f:
        rows = list(DictReader(f, dialect="excel-tab"))
        f.close()
    return rows


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
    logging.info(f"Soft assay endpoint response: {response.json()}")
    return response.json()


def read_rows(path: Path, encoding: str) -> list:
    message = None
    if not Path(path).exists():
        raise TSVError(f"File does not exist: {str(path)}")
    try:
        rows = dict_reader_wrapper(path, encoding)
        if not rows:
            message = f"File has no data rows: {path}"
        else:
            return rows
    except IsADirectoryError:
        message = f"Expected a TSV, but found a directory: {path}"
    except UnicodeDecodeError as e:
        message = f"Decode Error: {get_context_of_decode_error(e)}"
    raise TSVError(message)


def get_data_dir_errors(
    dir_schema: str,
    root_path: Path,
    data_dir_path: Path,
    dataset_ignore_globs: list[str] = [],
) -> dict[str, dict | str]:
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

    if not possible_schemas:
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
        message = f"Invalid latest_version_name {latest_version_name}: {ke}"
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
            raise TSVError(
                f"Error occurred while gathering schemas for schema {schema_version}: {schema_details['errorMessage']}"
            )
        for schema in schema_details["resources"]:
            if schema[latest_version_name.value]:
                latest_schema_version = schema["@id"].removeprefix(CEDAR_SINGLE_TEMPLATE_URL_BASE)
            break
        return latest_schema_version

    except TSVError as te:
        raise te
    except Exception as e:
        logging.exception(f"Exception while gathering schemas for schema {schema_version}. {e}")
        message = f"Exception while gathering schemas for schema {schema_version}: {e}"
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
    tsv_path: str | Path,
    ignore_deprecation: bool = False,
    report_type: ReportType = ReportType.STR,
    globus_token: str = "",
    app_context: dict = {},
    *args,
    **kwargs,
) -> list:

    logging.info(f"Validating TSV...")
    try:
        schema = create_schema_for_entity_type(
            Path(tsv_path),
            Path(tsv_path).parent,
            token=globus_token,
            app_context=app_context,
            report_type=report_type,
            ignore_deprecation=ignore_deprecation,
            *args,
            **kwargs,
        )
    except PreflightError as e:
        # Return preflight errors to prevent uncaught exceptions downstream
        return [str(e)]
    if errors := schema.validate():
        return errors
    return []


def cedar_validation_call(tsv_path: str | Path) -> requests.models.Response:
    with open(tsv_path, "rb") as f:
        try:
            response = requests.post(
                CEDAR_VALIDATION_URL,
                files={"input_file": f},
            )
            response.raise_for_status()
            response_json = response.json()
            logging.info(f"Response: {response_json}")
        except Exception as e:
            raise RuntimeError(
                f"Spreadsheet Validator API request for {tsv_path} failed! Exception: {e}"
            ) from e
        logging.info(
            f"""
            CEDAR response for {tsv_path}:
            Schema: {response_json.get('schema', {}).get('name')}
            Reporting: {response_json.get('reporting')}
            """
        )
    return response


def get_entity_api_data(
    entity_api_url: str,
    entity_id: str,
    globus_token: str,
    headers: dict | None = None,
) -> requests.Response:
    if not globus_token:
        raise Exception("No token received to check URL fields against Entity API.")
    if not headers:
        headers = {}
    headers["Authorization"] = f"Bearer {globus_token}"
    if not entity_api_url.endswith("/"):
        entity_api_url = entity_api_url + "/"
    url = urljoin(entity_api_url, entity_id)
    encoded_params = urlencode({"exclude": "direct_ancestors.files"})
    url += f"?{encoded_params}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response


def get_entity_info_from_entity_api(
    entity_url: str,
    entity_id: str,
    globus_token: str,
    headers: dict | None = None,
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
    error: str, row: str | None = None, column: str | None = None
) -> dict[str, str | None]:
    return {
        "column": column,
        "error": error,
        "row": row,
    }


def get_message(error: dict[str, str], report_type: ReportType = ReportType.STR) -> str | dict:
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


def referenced_paths_by_tsv(
    col_name: str, tsv_path: Path, rows: list
) -> dict[str, list[tuple[str, int]]]:
    """
    Returns dict of {path: [(referencing_tsv_path, row)]}
    (col_name is already available wherever this was called)
    """
    references = defaultdict(list)
    for i, row in enumerate(rows):
        if path_value := row.get(col_name):
            references[path_value].append((tsv_path, i + 2))
    return dict(references)


def format_error(e: Exception, fieldname: str, row: int, value):
    return {
        "errorType": type(e).__name__,
        "column": fieldname,
        "row": row,
        "value": value,
        "error_text": e.__str__(),
    }


@dataclass
class EntityTypeInfo:
    entity_type: EntityTypes
    entity_subtype: str = ""
    entity_subtype_val: str = ""

    def __post_init__(self):
        if (
            self.entity_type in [OtherTypes.SAMPLE, DatasetType.DATASET]
            and not self.entity_sub_type
        ):
            raise Exception(f"Entity of type {self.entity_type} must have a sub_type.")
        # If a member of the Sample enum is passed in as the entity_type,
        # this extracts the entity_type and entity_sub_type from that value
        # and mutates the instance accordingly
        # e.g. self.entity_type == <Sample.BLOCK: "sample-block">
        if isinstance(self.entity_type, Sample):
            self.entity_sub_type = self.entity_type.name.lower()
            self.entity_type = OtherTypes.SAMPLE
        if self.entity_sub_type == Sample.ORGAN and not self.entity_subtype_val:
            raise Exception(
                f"Entity of type {self.entity_type}/{self.entity_sub_type} must have a sub_type_val."
            )

    def format_constraint_check_data(self) -> dict:
        """
        Formats data about an entity so that it can be sent as
        part of the payload to the constraints endpoint.
        """
        return {
            "entity_type": self.entity_type.value,
            "sub_type": [self.entity_subtype] if self.entity_subtype else None,
            "sub_type_val": ([self.entity_subtype_val] if self.entity_subtype_val else None),
        }

    def format_constraint_check_error(self):
        data_entity_sub_type = f"/{self.entity_subtype.lower()}" if self.entity_subtype else ""
        data_entity_sub_type_val = (
            f"/{self.entity_subtype_val.lower()}" if self.entity_subtype_val else ""
        )
        return self.entity_type + data_entity_sub_type + data_entity_sub_type_val


@dataclass
class AncestorTypeInfo(EntityTypeInfo):
    entity_id: str = ""
    source_schema: Schema | None = None
    row: int | None = None
    column: str = ""
