from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Union
from urllib.parse import urlsplit

from ingest_validation_tools.enums import UNIQUE_FIELDS_MAP, DatasetType, OtherTypes
from ingest_validation_tools.error_report import ErrorDict, InfoDict, serialize
from ingest_validation_tools.schema_loader import (
    AncestorTypeInfo,
    EntityTypeInfo,
    PreflightError,
)
from ingest_validation_tools.table_validator import ReportType


@dataclass
class ValidationEntity:
    path: Union[str, Path]
    globus_token: str = ""
    app_context: Optional[dict] = None
    report_type: ReportType = ReportType.STR
    # TODO: does this even work
    verbose: bool = True

    def __post_init__(self):
        self.errors = ErrorDict()
        self.get_errors_called = False
        self.path = Path(self.path)
        if not self.path.exists:
            # TODO: need to fix errordict, and create enums to use for keys instead
            self.errors["Preflight"] = f"Invalid path: {self.path}"
        self.app_context = self.get_app_context(self.app_context if self.app_context else {})
        self.check_fields = [
            "parent_sample_id",
            "parent_dataset_id",
            "source_id",
            "sample_id",
        ]
        self.tsvs = []
        self.app_context_defaults = {
            "entities_url": "https://entity.api.hubmapconsortium.org/entities/",
            "ingest_url": "https://ingest.api.hubmapconsortium.org/",
            "request_header": {"X-Hubmap-Application": "ingest-pipeline"},
            "constraints_url": None,
        }

    def get_app_context(self, submitted_app_context: Optional[dict]):
        """
        Ensure that all default values are present, but privilege any
        submitted values (after making a basic validity check).
        """
        # TODO: should use env vars here
        if not submitted_app_context:
            return self.app_context_defaults
        for url_type in ["entities_url", "ingest_url", "constraints_url"]:
            if submitted_app_context.get(url_type):
                split_url = urlsplit(submitted_app_context[url_type])
                assert (
                    split_url.scheme and split_url.netloc
                ), f"{url_type} URL is incomplete: {submitted_app_context[url_type]}"
        return self.app_context_defaults | submitted_app_context


class SingleTSV(ValidationEntity):
    """
    Values can be set manually but likely these SingleTSV values will be derived.
    """

    schema_name: Optional[str] = None  # Valid values: canonical assay name OR other type
    version: str = ""
    directory_path: Optional[Path] = None
    rows: list = field(default_factory=list)
    soft_assay_data: dict = field(default_factory=dict)
    is_cedar: bool = True
    # TODO: rethink how this works with sample etc.
    dataset_type: str = ""  # String from assay_type or dataset_type field in TSV
    # TODO: enum
    metadata_type: str = "assays"
    contains: list = field(default_factory=list)
    entity_type_info: Optional[EntityTypeInfo] = None
    ancestor_entities: list[AncestorTypeInfo] = field(default_factory=list)
    validator_class: Validator = SingleTSVValidator
    # TODO: local validation artifacts--pull into separate class/roll into kwargs?
    table_schema: str = ""
    optional_fields: list = field(default_factory=list)
    dataset_ignore_globs: list = field(default_factory=list)
    ignore_deprecation: bool = False

    ################
    # Setup values #
    ################

    def __post_init__(self):
        super().__post_init__()
        self.name = "tsv"
        # TODO: get schema_name
        if self.schema_name in OtherTypes.with_sample_subtypes():
            self.metadata_type = "others"
        self.get_row_data()
        self.get_assayclassifier_data()
        if not self.is_cedar:
            self._get_table_schema_info()
            self.validator_class = LocalValidator

    def get_row_data(self):
        if not self.rows:
            # TODO: get rows
            return
        if not (metadata_schema_id := self.rows[0].get("metadata_schema_id")):
            self.is_cedar = False
        self.get_dataset_type_value()
        if self.is_cedar:
            self.version = metadata_schema_id
        else:
            self.version = self.rows[0].get("version", "0")

    def get_assayclassifier_data(self):
        self.dir_schema = self.soft_assay_data.get("dir-schema")
        contains = self.soft_assay_data.get("must-contain")
        if contains:
            self.contains = [schema.lower() for schema in contains]

    # TODO: what are we doing here
    def get_dataset_type_value(self):
        dataset_fields = {
            k: v for k, v in self.rows[0].items() if k in UNIQUE_FIELDS_MAP[DatasetType.DATASET]
        }
        values_found = list(dataset_fields.values())
        if len(values_found) == 0:
            return
        elif len(values_found) > 1:
            raise PreflightError(
                f"Found multiple dataset fields for path {self.path}: {dataset_fields}"
            )
        self.dataset_type = values_found[0]

    # TODO: local validation artifact
    def _get_table_schema_info(self):
        if self.is_cedar:
            return
        table_schema = self.soft_assay_data.get("tbl-schema")
        if not table_schema:
            self.table_schema = f"{self.schema_name}-v{self.version}"
        elif self.table_schema.endswith("v"):
            self.table_schema = self.table_schema + str(self.version)
        else:
            raise PreflightError(
                f"No table_schema for upload at {self.directory_path}. Schema: {self.schema_name}. Version: {self.version}."
            )

    ##############
    # Validation #
    ##############

    def validate(self):
        pass


class Upload(ValidationEntity):
    plugin_directory: Optional[Path] = None
    encoding: str = "utf-8"
    extra_parameters: Union[dict, None] = None
    run_plugins: Optional[bool] = None
    validator_class: Validator = UploadValidator
    # TODO: reconsider
    no_url_checks: bool = False
    # TODO: local validation artifact
    upload_ignore_globs: list = field(default_factory=list)
    # Get dir schema, check is_multi_assay/is_shared_upload, find/instantiate/validate singletsvs, set self.contributors?, self.antibodies?
    # Does the upload itself have a name/type? e.g. its repr

    def __post_init__(self):
        super().__post_init__()
        self.name = "upload"
        self.metadata_tsvs: list[SingleTSV] = []
        self.is_multi_assay: Optional[bool] = None
        self.info = InfoDict()
        self.get_info_called: bool = False

    def validate(self):
        pass


# validate("tsv"|"upload", path, globus_token, app_context, **kwargs)
def validate(entity_type, path, globus_token, app_context, report_type, **kwargs):
    """
    User-facing method.
    """
    # TODO: magic strings
    if entity_type == "upload":
        # check req kwargs are present
        validation_class = Upload
    elif entity_type == "tsv":
        # check req kwargs are present
        validation_class = SingleTSV
    else:
        return "Invalid entity type passed."
    errors = validation_class(path, globus_token, app_context, **kwargs).validate()
    return serialize(errors, report_type)
