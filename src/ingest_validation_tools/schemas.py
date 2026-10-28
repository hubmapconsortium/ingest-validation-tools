from __future__ import annotations

from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path

from ingest_validation_tools.enums import (
    UNIQUE_FIELDS_MAP,
    DatasetType,
    EntityTypes,
    OtherTypes,
    ReportType,
    Sample,
)
from ingest_validation_tools.schema_loader import PreflightError
from ingest_validation_tools.schema_validators import SupportSchemaValidator
from ingest_validation_tools.validation_utils import (
    AncestorTypeInfo,
    EntityTypeInfo,
    TSVError,
    format_error,
    get_assaytype_data,
    get_entity_api_data,
    get_entity_type_vals,
    get_message,
    read_rows,
)


@dataclass
class Schema:
    path: Path
    base_dir: Path
    entity_type: EntityTypes  # maps to schema_name
    token: str
    app_context: dict[str, str] = {}
    entity_url: str = ""
    ingest_url: str = ""
    report_type: ReportType = ReportType.JSON
    rows: list = field(default_factory=list)
    is_cedar: bool = False
    version: str = ""
    soft_assay_data: dict = field(default_factory=dict)
    ancestor_entities: list[AncestorTypeInfo] = field(default_factory=list)
    table_schema: str = ""  # legacy only
    ignore_deprecation: bool = False  # legacy only

    ancestor_fields = []

    def __post_init__(self):
        self.errors = []
        self.parse_app_context()
        self.get_entity_type_info()
        self.get_row_data()
        self.get_table_schema()
        self.get_ancestors()

    @cached_property
    def validator(self):
        raise NotImplementedError()

    def validate(self):
        if self.validator:
            errors = self.validator(self).validate()
            return self.errors | errors
        return self.errors

    def parse_app_context(self):
        self.entity_url = self.app_context.get("entities_url", "")
        self.ingest_url = self.app_context.get("ingest_url", "")
        self.constraints_url = self.app_context.get("constraints_url", "")
        for url_type in ["entities_url", "ingest_url"]:
            if not url_type:
                raise PreflightError(f"Required URL {url_type} not provided, can't create schema.")

    def get_entity_type_info(self):
        raise NotImplementedError()

    def get_row_data(self):
        if not self.rows:
            self.rows = read_rows(self.path, "utf-8")
        if self.rows[0].get("metadata_schema_id"):
            self.is_cedar = True
        else:
            self.is_cedar = False
        if self.is_cedar:
            self.version = self.rows[0].get("metadata_schema_id")
        else:
            self.version = self.rows[0].get("version", "0")

    def get_table_schema(self):
        if self.is_cedar:
            return
        self.table_schema = f"{self.entity_type}-v{self.version}"

    @cached_property
    def entity_type_info(self):
        return EntityTypeInfo(self.entity_type.value)

    @cached_property
    def ancestor_field_values(self) -> dict:
        for row in self.rows:
            return {
                k: (i, v.split(","))
                for i, (k, v) in enumerate(row.items())
                if k in self.ancestor_fields
            }
        return {}

    def get_ancestors(self):
        for fieldname, (row, value) in self.ancestor_field_values.items():
            response = get_entity_api_data(self.entity_url, value, self.token)
            try:
                self.get_ancestor(fieldname, row, value, response.json())
            except Exception as e:
                error = format_error(e, fieldname, row, value)
                self.errors.append(get_message(error, self.report_type))

    def get_ancestor(
        self, fieldname: str, row: int, value: str, response: dict
    ) -> AncestorTypeInfo | None:
        entity_type_vals = get_entity_type_vals(response)
        # Do not get ancestor info for sample (no subtype) or source
        if (
            entity_type_vals[0] == OtherTypes.SAMPLE and not entity_type_vals[1]
        ) or entity_type_vals[0] == OtherTypes.SOURCE:
            return
        self.ancestor_entities.append(
            AncestorTypeInfo(
                entity_id=value,
                row=row,
                column=fieldname,
                *entity_type_vals,
            )
        )


@dataclass
class SupportSchema(Schema):
    @cached_property
    def validator(self):
        return SupportSchemaValidator(self, self.report_type)


@dataclass
class SampleSchema(Schema):
    ancestor_fields = ["source_id", "sample_id", "organ_id"]

    @cached_property
    def validator(self):
        return SupportSchemaValidator(self, self.report_type)

    @property
    def entity_id(self) -> str:
        _, unique_field = match_tsv_type(self.rows)
        return self.rows[0][unique_field]

    @cached_property
    def entity_type_info(self):
        """
        Make an entity-api call and from the response, get
        entity_type, subtype data (e.g. "block" for sample), and
        any sub_type_val values (currently just organ codes, e.g. "BD").
        """
        response = get_entity_api_data(self.entity_url, self.entity_id, self.token).json()
        entity_type, entity_subtype, entity_subtype_val = get_entity_type_vals(response)
        if not entity_subtype:
            self.errors.append(f"Sample entities must have a sub_type.")
        elif entity_subtype == Sample.ORGAN:
            if not (val := response.get("organ", "").lower()):
                self.errors.append(
                    f"Entity of type {entity_type}/{entity_subtype} must have a sub_type_val."
                )
            entity_subtype_val = val
        return EntityTypeInfo(entity_type, entity_subtype, entity_subtype_val)


@dataclass
class DatasetSchema(Schema):
    dataset_type: str = ""  # String from assay_type or dataset_type field in TSV
    contributors_schemas: list[SupportSchema] = field(default_factory=list)
    antibodies_schemas: list[SupportSchema] = field(default_factory=list)
    dir_schema: str = ""
    is_multi_assay_parent: bool = False
    is_multi_assay_child: bool = False
    contains: list[DatasetSchema] = field(default_factory=list)

    def validate(self):
        super().validate()
        self.get_assayclassifier_data()
        self.get_dataset_type()

    def validate_rows(self):
        for required_field in ["data_path", "contributors_path"]:
            if required_field not in self.rows[0]:
                self.errors.append(f"File is missing required field {required_field}.")

    def get_assayclassifier_data(self):
        self.soft_assay_data = get_assaytype_data(self.rows[0], self.ingest_url, self.token)
        message = []
        if not self.soft_assay_data:
            message.append(f"No match found in assayclassifier for TSV {self.path}.")
            if "assay_type" in self.rows[0]:
                message.append(f'Assay type: {self.rows[0].get("assay_type")}.')
            elif "dataset_type" in self.rows[0]:
                message.append(
                    f'Dataset type: {self.rows[0].get("dataset_type")}. Data Curator: check Pipeline Decision Rules to determine correct Assay Type and make sure metadata TSV matches the specification for that type.'
                )
            raise PreflightError(" ".join([msg for msg in message]))
        self.schema_type = self.soft_assay_data["assaytype"]
        self.dir_schema = self.soft_assay_data.get("dir-schema", "")
        if contains := self.soft_assay_data.get("must-contain"):
            self.contains = [schema.lower() for schema in contains]
            self.is_multi_assay_parent = True

    def get_dataset_type(self) -> str | None:
        """
        Pull dataset_type or assay_type string from TSV.
        """
        dataset_fields = {
            k: v for k, v in self.rows[0].items() if k in UNIQUE_FIELDS_MAP[DatasetType.DATASET]
        }
        values_found = list(dataset_fields.values())
        if len(values_found) == 0:
            raise PreflightError(
                f"Could not identify dataset_type or assay_type for TSV {self.path}"
            )
        elif len(values_found) > 1:
            raise PreflightError(
                f"Found multiple dataset fields for TSV {self.path}: {dataset_fields}"
            )
        self.dataset_type = values_found[0]

    def get_table_schema(self):
        if self.is_cedar:
            return
        if table_schema := self.soft_assay_data.get("tbl-schema"):
            self.table_schema = (
                table_schema
                if not table_schema.endswith("v")
                else table_schema + str(self.version)
            )
        else:
            super().get_table_schema()

    def get_supporting_schemas(self):
        for other_type in ["antibodies_path", "contributors_path"]:
            for path_value, row in self.data_paths.items():
                other_path = self.base_dir / path_value
                try:
                    assert other_path.exists()
                except AssertionError:
                    self.errors.append(
                        f'On row(s) {row}, column "{other_type}", value "{path_value}" points to non-existent file "{other_path}"'
                    )
                    continue
                supporting_schema = create_schema_for_entity_type(
                    other_path, self.base_dir, token=self.token, app_context=self.app_context
                )
                if isinstance(supporting_schema, SupportSchema):
                    if supporting_schema.entity_type is OtherTypes.CONTRIBUTORS:
                        self.contributors_schemas.append(supporting_schema)
                    elif supporting_schema.entity_type is OtherTypes.ANTIBODIES:
                        self.antibodies_schemas.append(supporting_schema)
                else:
                    raise PreflightError(
                        f"Found reference to schema type '{supporting_schema.entity_type.value}' in TSV {self.path}."
                    )

    ancestor_fields = ["parent_sample_id", "parent_dataset_id"]

    def get_antibodies_schemas(self):
        pass

    @cached_property
    def data_paths(self) -> dict[Path, int]:
        # TODO: would be different for shared upload
        data_paths = {}
        if all("data_path" in row for row in self.rows):
            for i, row in enumerate(self.rows):
                data_path = Path(row["data_path"])
                if not data_path.is_absolute():
                    data_path = self.path.parent / data_path
                if not data_path.is_dir():
                    self.errors.append(f"{data_path} should be the base directory of a dataset")
                    continue
                data_paths[data_path] = i
            print(f"Data paths being passed to plugins: {data_paths}")
        else:
            self.errors.append(f"{self.path} is missing values in 'data_path' column")
        return data_paths


def create_schema_for_entity_type(
    path: Path, base_dir: Path, token: str, app_context: dict, *args, **kwargs
) -> Schema:
    """
    Determine entity type from fields in TSV and create appropriate
    Schema object.
    """
    try:
        rows = read_rows(path, "utf-8")
    except TSVError as e:
        raise PreflightError(e.errors)
    tsv_type, _ = match_tsv_type(rows)
    match tsv_type:
        case DatasetType.DATASET:
            schema_class = DatasetSchema
        case OtherTypes.ANTIBODIES | OtherTypes.CONTRIBUTORS:
            schema_class = SupportSchema
        case OtherTypes.ORGAN | OtherTypes.SOURCE | OtherTypes.SAMPLE:
            schema_class = SampleSchema
    return schema_class(
        path,
        base_dir=base_dir,
        entity_type=tsv_type,
        token=token,
        app_context=app_context,
        rows=rows,
        *args,
        **kwargs,
    )


def match_tsv_type(rows: list) -> tuple[EntityTypes, str]:
    entity_type_matches = []
    field_matches = []
    for entity_type, unique_fields in UNIQUE_FIELDS_MAP.items():
        for fieldname in rows[0].keys():
            if fieldname in unique_fields:
                entity_type_matches.append(entity_type)
                field_matches.append(fieldname)
    if len(field_matches) > 1:
        raise PreflightError(f"Multiple entity type fields found: {', '.join(field_matches)}.")
    elif len(entity_type_matches) == 0:
        raise PreflightError(f"Could not determine entity type.")
    return entity_type_matches[0], field_matches[0]
