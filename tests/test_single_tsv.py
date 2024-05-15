import json
import unittest
from pathlib import Path
from unittest.mock import patch

import requests
from parameterized import parameterized

from ingest_validation_tools.table_validator import ReportType
from ingest_validation_tools.upload import Upload
from ingest_validation_tools.validation_utils import get_schema_version, get_tsv_errors
from tests.fixtures import (
    BAD_DATASET_EXPECTED_PAYLOAD,
    BAD_DATASET_SCHEMA,
    GOOD_DATASET_EXPECTED_PAYLOAD,
    GOOD_DATASET_SCHEMA,
    SAMPLE_BLOCK_CONSTRAINTS_RESPONSE_BAD,
    SAMPLE_BLOCK_CONSTRAINTS_RESPONSE_GOOD,
    SAMPLE_BLOCK_PARTIAL_CEDAR_RESPONSE_GOOD,
    SAMPLE_BLOCK_PARTIAL_ENTITY_API_RESPONSE,
    SAMPLE_ORGAN_PARTIAL_ENTITY_API_RESPONSE,
    TEST_GET_TSV_ERRORS_PARAMS,
)

CONSTRAINTS_URL_PARAMS = "match=True&order=ancestors"
CONSTRAINTS_URL = "http://constraints_test/"
ENTITIES_URL = "http://entities_test/"


def entity_api_side_effect(response_map, url, globus_token, headers):
    del globus_token, headers
    return get_mock_response(True, response_map.get(url))


def get_mock_response(good: bool, response_data: bytes):
    mock_resp = requests.models.Response()
    mock_resp.url = CONSTRAINTS_URL
    mock_resp.status_code = 200 if good else 400
    mock_resp.reason = "OK" if good else "Bad Request"
    mock_resp._content = response_data
    return mock_resp


class TestSingleTsv(unittest.TestCase):

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
        payload = upload._construct_constraint_check(BAD_DATASET_SCHEMA)
        assert payload == BAD_DATASET_EXPECTED_PAYLOAD

    def test_good_payload(self):
        upload = self.get_upload
        payload = upload._construct_constraint_check(GOOD_DATASET_SCHEMA)
        assert payload == GOOD_DATASET_EXPECTED_PAYLOAD

    @patch("ingest_validation_tools.upload.requests.post")
    def test_constraints_bad(self, mock_request):
        upload = self.get_upload
        mock_request.return_value = get_mock_response(False, SAMPLE_BLOCK_CONSTRAINTS_RESPONSE_BAD)
        self.assertEqual(
            upload._constraint_checks(BAD_DATASET_SCHEMA),
            [
                "Invalid ancestor type for TSV type dataset/histology. Data sent for ancestor test_id_1: publication/."
            ],
        )
        data = [value for value in BAD_DATASET_EXPECTED_PAYLOAD.values()]
        mock_request.assert_any_call(
            CONSTRAINTS_URL + CONSTRAINTS_URL_PARAMS,
            headers={"Authorization": "Bearer test", "Content-Type": "application/json"},
            data=json.dumps(data),
        )

    @patch("ingest_validation_tools.upload.requests.post")
    def test_constraints_good(self, mock_request):
        upload = self.get_upload
        mock_request.return_value = get_mock_response(True, SAMPLE_BLOCK_CONSTRAINTS_RESPONSE_GOOD)
        # Shouldn't return anything
        upload._constraint_checks(GOOD_DATASET_SCHEMA)
        data = [value for value in GOOD_DATASET_EXPECTED_PAYLOAD.values()]
        mock_request.assert_any_call(
            CONSTRAINTS_URL + CONSTRAINTS_URL_PARAMS,
            headers={"Authorization": "Bearer test", "Content-Type": "application/json"},
            data=json.dumps(data),
        )

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

    @property
    def entity_api_response_map(self) -> dict[str, bytes]:
        return {
            f"{ENTITIES_URL}HBM233.CGGG.482": SAMPLE_BLOCK_PARTIAL_ENTITY_API_RESPONSE,
            f"{ENTITIES_URL}HBM724.ZQKX.379": SAMPLE_BLOCK_PARTIAL_ENTITY_API_RESPONSE,
            f"{ENTITIES_URL}HBM733.HSZF.798": SAMPLE_ORGAN_PARTIAL_ENTITY_API_RESPONSE,
        }

    @parameterized.expand(TEST_GET_TSV_ERRORS_PARAMS)
    def test_get_other_tsv_errors(
        self,
        good: bool,
        constraint_checks_response: bytes,
        cedar_response: bytes,
        path: str,
        schema_name: str,
        expected_errors: list,
    ):
        with patch("ingest_validation_tools.upload.requests.post") as mock_constraints_response:
            with patch("ingest_validation_tools.upload.cedar_api_call") as mock_cedar_call:
                with patch(
                    "ingest_validation_tools.validation_utils.get_entity_api_data",
                    side_effect=lambda url, globus_token, headers=None: entity_api_side_effect(
                        self.entity_api_response_map, url, globus_token, headers
                    ),
                ):
                    with patch(
                        "ingest_validation_tools.upload.get_entity_api_data",
                        side_effect=lambda url, globus_token, headers=None: entity_api_side_effect(
                            self.entity_api_response_map, url, globus_token, headers
                        ),
                    ):
                        mock_cedar_call.return_value = get_mock_response(True, cedar_response)
                        mock_constraints_response.return_value = get_mock_response(
                            good, constraint_checks_response
                        )
                        errors = get_tsv_errors(
                            Path(path).absolute(),
                            schema_name,
                            globus_token="test",
                            app_context={
                                "entities_url": ENTITIES_URL,
                                "constraints_url": CONSTRAINTS_URL,
                            },
                            report_type=ReportType.JSON,
                        )
                        assert errors == expected_errors


# if __name__ == "__main__":
#     suite = unittest.TestLoader().loadTestsFromTestCase(TestSingleTsv)
#     suite.debug()
