import json
import unittest
from pathlib import Path
from unittest.mock import patch

import requests

from ingest_validation_tools.schema_loader import SchemaVersion
from ingest_validation_tools.upload import Upload

from .fixtures import CONSTRAINTS_RESPONSE_BAD, CONSTRAINTS_RESPONSE_GOOD


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

    def setUp(self):
        self.constraints_url = "http://test"
        self.upload = Upload(directory_path=Path("."))
        self.upload.app_context = {"constraints_url": self.constraints_url}
        self.upload.verbose = False

    def get_mock_response(self, status_code: int, reason: str, response_data):
        mock_resp = requests.models.Response()
        mock_resp.url = self.upload.app_context["constraints_url"]
        mock_resp.status_code = status_code
        mock_resp.reason = reason
        mock_resp._content = response_data
        return mock_resp

    def test_bad_payload(self):
        payload = self.upload._construct_constraint_check(self.bad_dataset_schema)
        assert payload == self.bad_dataset_expected_payload

    def test_good_payload(self):
        payload = self.upload._construct_constraint_check(self.good_dataset_schema)
        assert payload == self.good_dataset_expected_payload

    @patch("ingest_validation_tools.upload.requests.request")
    def test_constraints_bad(self, mock_request):
        mock_request.return_value = self.get_mock_response(
            400, "Bad Request", CONSTRAINTS_RESPONSE_BAD
        )
        # Should raise Exception because of 400 response
        self.assertRaises(Exception, self.upload._constraint_checks, *[self.bad_dataset_schema])
        mock_request.assert_any_call(
            "POST",
            self.constraints_url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(self.bad_dataset_expected_payload),
        )

    @patch("ingest_validation_tools.upload.requests.request")
    def test_constraints_good(self, mock_request):
        mock_request.return_value = self.get_mock_response(200, "OK", CONSTRAINTS_RESPONSE_GOOD)
        # Shouldn't return anything
        self.upload._constraint_checks(self.good_dataset_schema)
        mock_request.assert_any_call(
            "POST",
            self.constraints_url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(self.good_dataset_expected_payload),
        )


# if __name__ == "__main__":
#     suite = unittest.TestLoader().loadTestsFromTestCase(TestSingleTsv)
#     suite.debug()
