import json
import logging
from abc import ABC
from functools import cached_property
from typing import TYPE_CHECKING

import requests

from ingest_validation_tools.enums import OtherTypes, ReportType
from ingest_validation_tools.local_validation.table_validator import get_table_errors
from ingest_validation_tools.schema_loader import get_table_schema
from ingest_validation_tools.validation_utils import (
    cedar_validation_call,
    find_empty_tsv_columns,
    format_error,
    get_entity_api_data,
    get_message,
)

if TYPE_CHECKING:
    from ingest_validation_tools.schemas import Schema

CONSTRAINTS_CHECK_METHOD = "ancestors"


class Validator(ABC):
    """
    Validator classes handle metadata validation and
    URL checks for each individual TSV.
    """

    metadata_errors = {}
    url_errors = []
    constraint_check_errors = []

    def __init__(self, schema: Schema, report_type: ReportType = ReportType.JSON):
        self.schema = schema
        self.report_type = report_type

    def validate(self, status_cache: dict):
        self.status_cache = status_cache
        self.validate_schema()
        self.check_urls()
        self.check_constraints()
        return self.compiled_errors()

    def compiled_errors(self):
        errors = {}
        errors["TSV errors"] = self.metadata_errors
        errors["URL errors"] = self.url_errors
        errors["Ancestor constraint errors"] = self.constraint_check_errors
        return errors

    #####################
    # Schema validation #
    #####################

    def validate_schema(self):
        if empty := find_empty_tsv_columns(self.schema.path):
            self.metadata_errors["Empty columns"] = {", ".join([str(i) for i in empty])}
        if not self.schema.is_cedar:
            logging.info(
                f"""TSV {self.schema.path} does not contain a metadata_schema_id,
                sending for local validation"""
            )
            self._local_validation()
        else:
            self._api_validation()

    def _local_validation(self):
        try:
            schema = get_table_schema(self.schema)
        except Exception as e:
            self.metadata_errors[self.schema.table_schema] = [str(e)]
            return
        if schema.get("deprecated") and not self.schema.ignore_deprecation:
            self.metadata_errors[self.schema.table_schema] = "Schema version is deprecated"
            return

        local_errors, new_status_cache = get_table_errors(
            self.schema.path, schema, self.status_cache
        )
        self.status_cache = new_status_cache
        if local_errors:
            self.metadata_errors[self.schema.table_schema] = local_errors

    def _api_validation(self) -> list[str | dict]:
        errors = []
        response = cedar_validation_call(self.schema.path)
        if response.status_code != 200:
            self.metadata_errors.append(response.status_code)
        elif response.json().get("reporting") and len(response.json().get("reporting")) > 0:
            for error in response.json()["reporting"]:
                errors.append(get_message(error, self.report_type))
        else:
            logging.info(f"No errors found during CEDAR validation for {self.schema.path}!")
            logging.info(f"Response: {response.json()}.")
        return errors

    ##############
    # URL checks #
    ##############

    url_check_fields: list = []

    @cached_property
    def url_check_values(self) -> dict:
        for row in self.schema.rows:
            return {
                k: (i, v) for i, (k, v) in enumerate(row.items()) if k in self.url_check_fields
            }
        return {}

    def check_urls(self):
        for fieldname, (row, value) in self.url_check_values.items():
            try:
                self.check_single_url_field(fieldname, row, value)
            except Exception as e:
                error = format_error(e, fieldname, row, value)
                self.url_errors.append(get_message(error, self.report_type))

    def check_single_url_field(self, fieldname: str, row: int, value: str):
        del fieldname, row, value
        pass

    #####################
    # Constraint checks #
    #####################

    def check_constraints(self):
        payload = self.construct_constraint_payload()
        if not payload:
            print(f"No constraint checks made for {self.schema.path}.")
            return
        data = json.dumps(payload)
        headers = {
            "Authorization": f"Bearer {self.schema.token}",
        }
        params = {"match": True, "order": CONSTRAINTS_CHECK_METHOD}
        response = requests.post(
            self.schema.constraints_url, headers=headers, data=data, params=params
        )
        try:
            response.raise_for_status()
        except Exception:
            self._get_constraint_check_errors(response)

    def construct_constraint_payload(self):
        payload = []
        descendant_data = self.schema.entity_type_info.format_constraint_check_data()
        for ancestor_entity in self.schema.ancestor_entities:
            payload.append(
                {
                    "ancestors": ancestor_entity.format_constraint_check_data(),
                    "descendants": descendant_data,
                }
            )
        return payload

    def _get_constraint_check_errors(self, response: requests.Response):
        if response.status_code == 400:
            for i, entity_check in enumerate(response.json().get("description", [])):
                if entity_check["code"] != 200:
                    ancestors = self.schema.ancestor_entities[i].format_constraint_check_error()
                    error = {
                        "errorType": "Invalid Ancestor",
                        "column": self.schema.ancestor_entities[i].column,
                        "row": self.schema.ancestor_entities[i].row,
                        "value": self.schema.ancestor_entities[i].entity_id,
                        "error_text": f"Invalid ancestor type for TSV type {self.schema.entity_type_info.format_constraint_check_error()}. Data sent for ancestor {self.schema.ancestor_entities[i].entity_id}: {ancestors}.",
                    }
                    self.constraint_check_errors.append(get_message(error, self.report_type))


class SupportSchemaValidator(Validator):

    def validate(self, status_cache):
        super().validate(status_cache)
        self.check_contact()

    def check_contact(self):
        if self.schema.entity_type is OtherTypes.CONTRIBUTORS:
            is_contact = [row.get("is_contact", "").lower() for row in self.schema.rows]
            if not ("yes" in is_contact) and not ("true" in is_contact):
                self.metadata_errors["Missing value"] = "No primary contact."

    ################
    # URL checking #
    ################

    url_check_fields = ["orcid", "orcid_id"]

    def check_single_url_field(self, fieldname, row, value, response):
        if fieldname == "orcid":
            url = "https://pub.orcid.org/v3.0/expanded-search/"
        else:
            url = "https://pub.orcid.org/v3.0/expanded-search/"
        response = requests.get(
            url, headers={"Accept": "application/json"}, params={"q": f"orcid:{value}"}
        )
        num_found = response.json().get("num-found")
        if num_found == 1:
            return
        elif num_found == 0:
            self.url_errors.append(f"On row {row}, ORCID {value} does not exist.")
        else:
            self.url_errors.append(f"On row {row}, found {num_found} matches for ORCID {value}.")


class SampleSchemaValidator(Validator):
    pass


class DatasetSchemaValidator(Validator):

    url_check_fields = ["parent_sample_id"]

    def check_single_url_field(self, fieldname, row, value):
        response = get_entity_api_data(self.schema.entity_url, value, self.schema.token).json()
        try:
            self._check_for_organ_other(response)
            self._check_parent_sample_entity_type(response)
        except Exception as e:
            error = format_error(e, fieldname, row, value)
            self.url_errors.append(get_message(error, self.report_type))

    def _check_for_organ_other(self, response: dict):
        """
        Ensure that ancestor of parent_sample_id is not Organ with subtype "Other."
        """
        origin_samples = response.get("origin_samples")
        if origin_samples is None and "direct_ancestor" in response:
            origin_samples = response["direct_ancestor"].get("origin_samples")
        if origin_samples is not None and isinstance(origin_samples, list):
            for origin_sample in origin_samples:
                if (
                    origin_sample.get("organ") == "OT"
                    or origin_sample.get("organ") == "UBERON:0010000"
                    or origin_sample.get("organ") is None
                ):
                    self.constraint_check_errors.append(
                        f"You are not allowed to register data against Sample {origin_sample.get('uuid')} with Organ Other. Please contact the respective help desk to ensure that appropriate support for your work can be provided."
                    )

    def _check_parent_sample_entity_type(self, response: dict):
        """
        Ensure that parent_sample_id is actually a sample.
        """
        entity_type = response.get("entity_type", "").lower()
        if entity_type != OtherTypes.SAMPLE:
            self.constraint_check_errors.append(
                f"parent_sample_id must reference a Sample entity, but received entity type '{entity_type}'."
            )
        sample_category = response.get("sample_category", "").lower()
        valid_categories = {"block", "suspension", "section"}
        if sample_category not in valid_categories:
            self.constraint_check_errors.append(
                f"parent_sample_id must reference a Sample of type Block, Suspension, or Section, but received sample type '{sample_category}'."
            )


class SharedDatasetSchemaValidator(DatasetSchemaValidator):
    pass


class MultiDatasetSchemaValidator(DatasetSchemaValidator):
    pass
