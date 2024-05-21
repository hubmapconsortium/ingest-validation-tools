import json
import logging
from collections import defaultdict
from csv import DictReader
from pathlib import Path, PurePath
from typing import Dict, List, Optional, Union

import requests

from ingest_validation_tools.directory_validator import (
    DirectoryValidationErrors,
    validate_directory,
)
from ingest_validation_tools.enums import DatasetType, EntityTypes, OtherTypes, Sample
from ingest_validation_tools.schema_loader import (
    EntityTypeInfo,
    PreflightError,
    SchemaVersion,
    get_possible_directory_schemas,
)
from ingest_validation_tools.table_validator import ReportType

UNIQUE_FIELDS_MAP = {
    OtherTypes.ANTIBODIES: {"antibody_rrid", "antibody_name"},
    OtherTypes.CONTRIBUTORS: {"orcid", "orcid_id"},
    DatasetType.DATASET: {"assay_type", "dataset_type"},
    OtherTypes.SOURCE: {"strain_rrid"},
    OtherTypes.ORGAN: {"organ_id"},  # Deprecated?
    OtherTypes.SAMPLE: {"sample_id"},
}
OTHER_FIELDS_UNIQUE_FIELDS_MAP = {
    k: v for k, v in UNIQUE_FIELDS_MAP.items() if not k == DatasetType.DATASET
}


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
        message.append(f"No assay_type or dataset_type in {path}.")
        if "channel_id" in rows[0]:
            message.append('Has "channel_id": Antibodies TSV found where metadata TSV expected.')
        elif "orcid_id" in rows[0]:
            message.append('Has "orcid_id": Contributors TSV found where metadata TSV expected.')
    if message:
        raise PreflightError(" ".join([msg for msg in message]))
    assay_type_data = get_assaytype_data(
        rows[0],
        ingest_url,
    )
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
                other_type_info.entity_type,
                directory_path=directory_path,
                path=path,
                rows=rows,
                entity_type_info=other_type_info,
            )
            return sv


def get_other_schema_data(
    row: dict, path: str, url: str, globus_token: str, entity_field_pair: tuple[EntityTypes, str]
) -> EntityTypeInfo:
    entity_type = entity_field_pair[0]
    unique_field = entity_field_pair[1]
    # Double check this is not a badly-formatted metadata.tsv
    if set(row.keys()).intersection(UNIQUE_FIELDS_MAP[DatasetType.DATASET]):
        raise PreflightError(f"Metadata TSV {path} contains invalid field: {unique_field}")
    if entity_type == OtherTypes.SAMPLE:
        # Sample types require additional data
        return get_entity_info_from_entity_api(url + row[unique_field], globus_token)
    else:
        return EntityTypeInfo(entity_type)


def get_assaytype_data(
    row: Dict,
    ingest_url: str,
) -> Dict:
    if not ingest_url:
        ingest_url = "https://ingest.api.hubmapconsortium.org/"
    response = requests.post(
        f"""{ingest_url.strip("/")}/assaytype""",
        headers={"Content-Type": "application/json"},
        data=json.dumps(row),
    )
    response.raise_for_status()
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
    root_path: Path,
    data_dir_path: Path,
    dataset_ignore_globs: List[str] = [],
) -> Dict[str, Union[str, List[str]]]:
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
        return {dir_schema: ["No matching directory schemas found."]}

    # Collect errors, discard if schema validates against a minor version
    errors = []

    # Make sure possible_schemas is sorted by key (descending) to evaluate highest minor version first
    for schema_name, schema in sorted(possible_schemas.items(), reverse=True):
        schema_errors = defaultdict(list)
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
                schema_errors[schema_name].append(schema_warning)
            else:
                schema_errors[schema_name].append(e.errors)
        except OSError as e:
            # If there are OSErrors and the schema is deprecated/draft...
            #    the OSErrors are more important.
            if isinstance(e, FileNotFoundError):
                raise FileNotFoundError()
            schema_errors[schema_name].append(f"{e.strerror}: {e.filename}")
        if schema_errors:
            errors.append(schema_errors)
            continue
        elif schema_warning:
            errors.append({schema_name: schema_warning})
            continue
        # Found a schema with no problems!
        # Throw away any found errors.
        return {schema_name: "No errors!"}
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


def get_other_names():
    return [
        p.stem.split("-v")[0] for p in (Path(__file__).parent / "table-schemas/others").iterdir()
    ]


def get_tsv_errors(
    tsv_path: Union[str, Path],
    schema_name: str,
    optional_fields: List[str] = [],
    no_url_checks: bool = False,
    ignore_deprecation: bool = False,
    report_type: ReportType = ReportType.STR,
    globus_token: str = "",
    app_context: Dict = {},
) -> List:
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
        optional_fields=optional_fields,
        globus_token=globus_token,
        no_url_checks=no_url_checks,
        ignore_deprecation=ignore_deprecation,
        app_context=app_context,
        report_type=report_type,
    )
    if schema_name in OtherTypes.value_list() or Sample.full_names_list():
        upload._check_other_path(str(tsv_path))
    else:
        upload.validation_routine()
    return upload.errors.tsv_only_errors_by_path(str(tsv_path))


def cedar_api_call(tsv_path: Union[str, Path]) -> requests.models.Response:
    with open(tsv_path, "rb") as f:
        file = {"input_file": f}
        headers = {"content_type": "multipart/form-data"}
        try:
            response = requests.post(
                "https://api.metadatavalidator.metadatacenter.org/service/validate-tsv",
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
    url: str,
    globus_token: str,
    headers: Optional[dict] = None,
) -> requests.Response:
    if not headers:
        headers = {}
    headers["Authorization"] = f"Bearer {globus_token}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response


def get_entity_info_from_entity_api(
    url: str,
    globus_token: str,
    headers: Optional[dict] = None,
) -> EntityTypeInfo:
    """
    Make an entity-api call and from the response, get
    entity_type, subtype data (e.g. "block" for sample), and
    any sub_type_val values (currently just organ codes, e.g. "BD")
    and return as a dict in the format expected by the constraints endpoint.
    """
    response = get_entity_api_data(url, globus_token, headers)
    entity_type, entity_sub_type, entity_sub_type_val = get_entity_type_vals(response.json())
    return EntityTypeInfo(entity_type, entity_sub_type, entity_sub_type_val)


def get_entity_type_vals(response: dict) -> tuple:
    entity_type = response.get("entity_type", "").lower()
    entity_sub_type = None
    entity_sub_type_val = None
    if entity_type == OtherTypes.SAMPLE:
        entity_type = OtherTypes.SAMPLE
        entity_sub_type = response.get("sample_category", "").lower()
        if entity_sub_type == Sample.ORGAN:
            entity_sub_type_val = response.get("organ", "").lower()
    elif entity_type == DatasetType.DATASET:
        entity_type = DatasetType.DATASET
        entity_sub_type = response.get("dataset_type", "")
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
) -> Dict[str, Optional[str]]:
    return {
        "column": column,
        "error": error,
        "row": row,
    }
