import json
import unittest
from pathlib import Path
from unittest.mock import patch

import requests

from ingest_validation_tools.schema_loader import SchemaVersion
from ingest_validation_tools.table_validator import ReportType
from ingest_validation_tools.upload import Upload
from ingest_validation_tools.validation_utils import (
    get_other_schema_name,
    get_schema_version,
    read_rows,
)

from .fixtures import *

CONSTRAINTS_URL = "http://constraints_test"
ENTITIES_URL = "http://entities_test"


def get_mock_response(upload, status_code: int, reason: str, response_data):
    mock_resp = requests.models.Response()
    mock_resp.url = upload.app_context["constraints_url"]
    mock_resp.status_code = status_code
    mock_resp.reason = reason
    mock_resp._content = response_data
    return mock_resp


def post_side_effect(upload: Upload, schema_type: str, good: bool, *args, **kwargs):
    del kwargs
    suffix = "GOOD" if good else "BAD"
    prefix = schema_type.replace("-", "_").upper()
    status_code = 200 if good else 400
    reason = "OK" if good else "Bad Request"
    if args[0] == CONSTRAINTS_URL:
        return get_mock_response(
            upload, status_code, reason, eval(f"{prefix}_CONSTRAINTS_RESPONSE_{suffix}")
        )
    elif args[0] == "https://api.metadatavalidator.metadatacenter.org/service/validate-tsv":
        return get_mock_response(
            upload, status_code, reason, eval(f"{prefix}_PARTIAL_RESPONSE_{suffix}")
        )


class TestSingleTsv(unittest.TestCase):

    # ancestor_entities created in Upload._find_and_check_url_fields
    # from entity-api responses
    good_dataset_schema = SchemaVersion(
        schema_name="histology",
        ancestor_entities={
            "test_id_1": {"entity_type": "dataset", "sub_type": [""], "sub_type_val": None},
            "test_id_2": {"entity_type": "dataset", "sub_type": [""], "sub_type_val": None},
        },
    )
    bad_dataset_schema = SchemaVersion(
        schema_name="histology",
        ancestor_entities={
            "test_id_1": {"entity_type": "dataset", "sub_type": [""], "sub_type_val": None},
            "test_id_2": {"entity_type": "publication", "sub_type": [""], "sub_type_val": None},
        },
    )
    # Expected payloads from Upload._construct_constraint_check
    bad_dataset_expected_payload = [
        {
            "ancestors": {"entity_type": "dataset", "sub_type": [""], "sub_type_val": None},
            "descendants": {"entity_type": "dataset", "sub_type": [""], "sub_type_val": None},
        },
        {
            "ancestors": {
                "entity_type": "publication",
                "sub_type": [""],
                "sub_type_val": None,
            },
            "descendants": {"entity_type": "dataset", "sub_type": [""], "sub_type_val": None},
        },
    ]
    good_dataset_expected_payload = [
        {
            "ancestors": {"entity_type": "dataset", "sub_type": [""], "sub_type_val": None},
            "descendants": {"entity_type": "dataset", "sub_type": [""], "sub_type_val": None},
        },
        {
            "ancestors": {"entity_type": "dataset", "sub_type": [""], "sub_type_val": None},
            "descendants": {"entity_type": "dataset", "sub_type": [""], "sub_type_val": None},
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

    # @patch(
    #     "ingest_validation_tools.upload.Upload._find_and_check_url_fields",
    #     side_effect=lambda rows, constrained_fields, schema, report_type: _construct_constraints_side_effect(
    #         schema, rows, constrained_fields, report_type
    #     ),
    # )
    # def test_bad_dataset_schema(self):
    #     pass
    #
    @patch("ingest_validation_tools.upload.requests.post")
    def test_constraints_bad(self, mock_request):
        upload = self.get_upload
        mock_request.return_value = get_mock_response(
            upload, 400, "Bad Request", CONSTRAINTS_RESPONSE_BAD
        )
        # Should raise Exception because of 400 response
        self.assertRaises(Exception, upload._constraint_checks, *[self.bad_dataset_schema])
        mock_request.assert_any_call(
            CONSTRAINTS_URL,
            headers={"Content-Type": "application/json"},
            data=json.dumps(self.bad_dataset_expected_payload),
        )

    @patch("ingest_validation_tools.upload.requests.post")
    def test_constraints_good(self, mock_request):
        upload = self.get_upload
        mock_request.return_value = get_mock_response(upload, 200, "OK", CONSTRAINTS_RESPONSE_GOOD)
        # Shouldn't return anything
        upload._constraint_checks(self.good_dataset_schema)
        mock_request.assert_any_call(
            CONSTRAINTS_URL,
            headers={"Content-Type": "application/json"},
            data=json.dumps(self.good_dataset_expected_payload),
        )

    @patch("ingest_validation_tools.validation_utils.cedar_api_call")
    def test_get_sample_block_entity_type_from_tsv(self, mock_api_call):
        upload = self.get_upload
        mock_api_call.return_value = get_mock_response(
            upload, 200, "OK", SAMPLE_BLOCK_PARTIAL_RESPONSE_GOOD
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
            }
        ]
        wrong_ancestor_entities = [
            {
                "entity_type": "sample",
                "sub_type": ["suspension"],
                "sub_type_val": None,
            }
        ]
        upload = self.get_upload
        mock_entity_api.return_value = get_mock_response(
            upload, 200, "OK", SAMPLE_BLOCK_PARTIAL_ENTITY_API_RESPONSE
        )
        mock_cedar_api.return_value = get_mock_response(
            upload, 200, "OK", SAMPLE_BLOCK_PARTIAL_RESPONSE_GOOD
        )
        path = Path("./tests/fixtures/sample-block-good.tsv").absolute()
        schema = get_schema_version(path, "ascii")
        upload._get_url_errors(str(path), schema, report_type=ReportType.STR)
        assert list(schema.ancestor_entities.values()) == expected_ancestor_entities
        assert list(schema.ancestor_entities.values()) != wrong_ancestor_entities

    # def test_sample_block_good(self):
    #     with patch(
    #         "ingest_validation_tools.validation_utils.cedar_api_call",
    #         return_value=self.get_mock_response(200, "OK", SAMPLE_BLOCK_PARTIAL_RESPONSE_GOOD),
    #     ):
    #         with patch(
    #             "ingest_validation_tools.upload.requests.post",
    #             return_value=self.get_mock_response(
    #                 200, "OK", SAMPLE_BLOCK_PARTIAL_ENTITY_API_RESPONSE
    #             ),
    #         ):
    #             errors = get_tsv_errors(
    #                 Path("./tests/fixtures/sample-block-good.tsv").absolute(),
    #                 "sample-block",
    #                 globus_token="AgJmmjzaQ8krvgny0OJ19D0eWB0nrq3r478anDVdGPOJgxNWbDf0C89YMYlle2E4l9nyK6oP2mYn5Ntq103Wntnyywq",
    #                 report_type=ReportType.JSON,
    #             )
    #
    # @patch("ingest_validation_tools.validation_utils.cedar_api_call")
    # def test_sample_block_bad(self, mock_api_call):
    #     mock_api_call.return_value = self.get_mock_response(
    #         400, "Bad Request", SAMPLE_BLOCK_PARTIAL_RESPONSE_BAD
    #     )
    #     errors = get_tsv_errors(
    #         Path("./tests/fixtures/sample-block-bad.tsv").absolute(),
    #         "sample-block",
    #         globus_token="test",
    #         report_type=ReportType.JSON,
    #     )
    #     breakpoint()
    #     assert errors == ""


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSingleTsv)
    suite.debug()
