import json
import unittest
from pathlib import Path
from unittest.mock import patch

import requests
from parameterized import parameterized

from ingest_validation_tools.schema_loader import SchemaVersion
from ingest_validation_tools.table_validator import ReportType
from ingest_validation_tools.upload import Upload
from ingest_validation_tools.validation_utils import (
    get_other_schema_name,
    get_schema_version,
    get_tsv_errors,
    read_rows,
)

from .fixtures import *

CONSTRAINTS_URL = "http://constraints_test"
ENTITIES_URL = "http://entities_test"


def get_mock_response(good: bool, response_data: bytes):
    mock_resp = requests.models.Response()
    mock_resp.url = CONSTRAINTS_URL
    mock_resp.status_code = 200 if good else 400
    mock_resp.reason = "OK" if good else "Bad Request"
    mock_resp._content = response_data
    return mock_resp


def post_side_effect(schema_type: str, good: bool, *args, **kwargs):
    del kwargs
    func_args = [*args]
    suffix = "GOOD" if good else "BAD"
    prefix = schema_type.replace("-", "_").upper()
    if "constraints" in func_args[0]:
        return get_mock_response(good, eval(f"{prefix}_CONSTRAINTS_RESPONSE_{suffix}"))
    elif func_args[0] == "https://api.metadatavalidator.metadatacenter.org/service/validate-tsv":
        # Spreadsheet Validator returns 200 even if errors
        return get_mock_response(True, eval(f"{prefix}_PARTIAL_CEDAR_RESPONSE_{suffix}"))


class TestSingleTsv(unittest.TestCase):

    # ancestor_entities created in Upload._find_and_check_url_fields
    # from entity-api responses
    # dataset-histology as ancestor of dataset-histology might be gibberish
    # but as far as the rules are concerned it is valid
    good_dataset_schema = SchemaVersion(
        schema_name="histology",
        metadata_type="assays",
        rows=[{"parent_sample_id": "doesn't_matter", "dataset_type": "histology"}],
        ancestor_entities={
            "test_id_0": {
                "entity_type": "dataset",
                "sub_type": ["histology"],
                "sub_type_val": None,
            },
            "test_id_1": {
                "entity_type": "dataset",
                "sub_type": ["histology"],
                "sub_type_val": None,
            },
        },
    )
    # bad case: publication cannot be ancestor of dataset
    bad_dataset_schema = SchemaVersion(
        schema_name="histology",
        metadata_type="assays",
        rows=[{"parent_sample_id": "doesn't_matter", "dataset_type": "histology"}],
        ancestor_entities={
            "test_id_1": {
                "entity_type": "dataset",
                "sub_type": ["histology"],
                "sub_type_val": None,
            },
            "test_id_2": {"entity_type": "publication", "sub_type": [""], "sub_type_val": None},
        },
    )
    # Expected payloads from Upload._construct_constraint_check
    good_dataset_expected_payload = [
        {
            "ancestors": {
                "entity_type": "dataset",
                "sub_type": ["histology"],
                "sub_type_val": None,
            },
            "descendants": {
                "entity_type": "dataset",
                "sub_type": ["histology"],
                "sub_type_val": None,
            },
        },
        {
            "ancestors": {
                "entity_type": "dataset",
                "sub_type": ["histology"],
                "sub_type_val": None,
            },
            "descendants": {
                "entity_type": "dataset",
                "sub_type": ["histology"],
                "sub_type_val": None,
            },
        },
    ]
    # bad case: publication cannot be ancestor of dataset
    bad_dataset_expected_payload = [
        {
            "ancestors": {
                "entity_type": "dataset",
                "sub_type": ["histology"],
                "sub_type_val": None,
            },
            "descendants": {
                "entity_type": "dataset",
                "sub_type": ["histology"],
                "sub_type_val": None,
            },
        },
        {
            "ancestors": {
                "entity_type": "publication",
                "sub_type": [""],
                "sub_type_val": None,
            },
            "descendants": {
                "entity_type": "dataset",
                "sub_type": ["histology"],
                "sub_type_val": None,
            },
        },
    ]

    @property
    def get_upload(self):
        upload = Upload(directory_path=Path("."))
        upload.app_context = {
            "constraints_url": CONSTRAINTS_URL,
            "entities_url": ENTITIES_URL,
        }
        upload.verbose = False
        upload.globus_token = "test"
        return upload

    def test_bad_payload(self):
        upload = self.get_upload
        payload = upload._construct_constraint_check(self.bad_dataset_schema)
        assert payload == self.bad_dataset_expected_payload

    def test_good_payload(self):
        upload = self.get_upload
        payload = upload._construct_constraint_check(self.good_dataset_schema)
        assert payload == self.good_dataset_expected_payload

    @patch("ingest_validation_tools.upload.requests.post")
    def test_constraints_bad(self, mock_request):
        upload = self.get_upload
        mock_request.return_value = get_mock_response(False, SAMPLE_BLOCK_CONSTRAINTS_RESPONSE_BAD)
        # Should raise Exception because of 400 response
        self.assertRaises(Exception, upload.constraint_checks, *[self.bad_dataset_schema])
        mock_request.assert_any_call(
            CONSTRAINTS_URL,
            headers={"Content-Type": "application/json"},
            data=json.dumps(self.bad_dataset_expected_payload),
        )

    @patch("ingest_validation_tools.upload.requests.post")
    def test_constraints_good(self, mock_request):
        upload = self.get_upload
        mock_request.return_value = get_mock_response(True, SAMPLE_BLOCK_CONSTRAINTS_RESPONSE_GOOD)
        # Shouldn't return anything
        upload.constraint_checks(self.good_dataset_schema)
        mock_request.assert_any_call(
            CONSTRAINTS_URL,
            headers={"Content-Type": "application/json"},
            data=json.dumps(self.good_dataset_expected_payload),
        )

    @patch("ingest_validation_tools.validation_utils.cedar_api_call")
    def test_get_sample_block_entity_type_from_tsv(self, mock_api_call):
        mock_api_call.return_value = get_mock_response(
            True, SAMPLE_BLOCK_PARTIAL_CEDAR_RESPONSE_GOOD
        )
        path = "./tests/fixtures/sample-block-good.tsv"
        assert (
            get_other_schema_name(
                read_rows(Path("./tests/fixtures/sample-block-good.tsv").absolute(), "ascii"), path
            )
            == "sample-block"
        )
        mock_api_call.assert_called_with(path)

    @patch("ingest_validation_tools.upload.requests.post")
    @patch("ingest_validation_tools.upload.requests.get")
    def test_expected_ancestor_entities_creation(self, mock_entity_api, mock_cedar_api):
        expected_ancestor_entities = [
            {
                "entity_type": "sample",
                "sub_type": ["block"],
                "sub_type_val": None,
            },
            {
                "entity_type": "sample",
                "sub_type": ["block"],
                "sub_type_val": None,
            },
        ]
        wrong_ancestor_entities = [
            {
                "entity_type": "sample",
                "sub_type": ["block"],
                "sub_type_val": None,
            },
            {
                "entity_type": "sample",
                "sub_type": ["suspension"],
                "sub_type_val": None,
            },
        ]
        upload = self.get_upload
        mock_entity_api.return_value = get_mock_response(
            True, SAMPLE_BLOCK_PARTIAL_ENTITY_API_RESPONSE
        )
        mock_cedar_api.return_value = get_mock_response(
            True, SAMPLE_BLOCK_PARTIAL_CEDAR_RESPONSE_GOOD
        )
        path = Path("./tests/fixtures/sample-block-good.tsv").absolute()
        schema = get_schema_version(path, "ascii")
        upload._get_url_errors(str(path), schema, report_type=ReportType.STR)
        assert list(schema.ancestor_entities.values()) == expected_ancestor_entities
        assert list(schema.ancestor_entities.values()) != wrong_ancestor_entities

    @parameterized.expand(
        [
            (
                True,
                [
                    SAMPLE_BLOCK_PARTIAL_ENTITY_API_RESPONSE,
                    SAMPLE_BLOCK_PARTIAL_ENTITY_API_RESPONSE,
                    SAMPLE_BLOCK_PARTIAL_ENTITY_API_RESPONSE,
                    SAMPLE_BLOCK_PARTIAL_ENTITY_API_RESPONSE,
                ],
                "./tests/fixtures/sample-block-good.tsv",
                "sample-block",
                [],
            ),
            (
                False,
                [
                    SAMPLE_BLOCK_PARTIAL_ENTITY_API_RESPONSE,
                    SAMPLE_BLOCK_PARTIAL_ENTITY_API_RESPONSE,
                    SAMPLE_ORGAN_PARTIAL_ENTITY_API_RESPONSE,
                    SAMPLE_ORGAN_PARTIAL_ENTITY_API_RESPONSE,
                ],
                "./tests/fixtures/sample-block-bad.tsv",
                "sample-block",
                [
                    'On row 0, column "processing_time_unit", value "min" fails because of error "notStandardTerm". Example: minute',
                    'On row 0, column "source_storage_duration_unit", value "min" fails because of error "notStandardTerm". Example: minute',
                ],
            ),
        ]
    )
    def test_get_tsv_errors(
        self,
        good: bool,
        check_url_get_response_list: list,
        path: str,
        schema_name: str,
        expected_errors: list,
    ):
        with patch(
            "ingest_validation_tools.upload.requests.post",
            side_effect=lambda *args, **kwargs: post_side_effect(
                schema_name, good, *args, **kwargs
            ),
        ):
            with patch("ingest_validation_tools.upload.requests.get") as mock_get:
                mock_get.side_effect = [
                    get_mock_response(True, response) for response in check_url_get_response_list
                ]
                errors = get_tsv_errors(
                    Path(path).absolute(),
                    schema_name,
                    globus_token="test",
                    report_type=ReportType.JSON,
                )
                assert errors == expected_errors


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSingleTsv)
    suite.debug()
