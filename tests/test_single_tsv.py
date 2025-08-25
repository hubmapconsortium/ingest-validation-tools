import json
import unittest
from pathlib import Path
from unittest.mock import patch

import requests
from parameterized import parameterized

from ingest_validation_tools.enums import DatasetType, OtherTypes, Sample
from ingest_validation_tools.local_validation.table_validator import ReportType
from ingest_validation_tools.schema_loader import EntityTypeInfo, SchemaVersion
from ingest_validation_tools.upload import Upload
from ingest_validation_tools.validation_utils import get_schema_version, get_tsv_errors
from tests.fixtures import (
    BAD_DATASET_CONSTRAINTS_RESPONSE,
    BAD_DATASET_EXPECTED_PAYLOAD,
    BAD_DATASET_SCHEMA_WITH_ANCESTORS,
    GOOD_DATASET_EXPECTED_PAYLOAD,
    GOOD_DATASET_SCHEMA_WITH_ANCESTORS,
    SAMPLE_BLOCK_CONSTRAINTS_RESPONSE_GOOD,
    SAMPLE_BLOCK_PARTIAL_CEDAR_RESPONSE_GOOD,
    SAMPLE_BLOCK_PARTIAL_ENTITY_API_RESPONSE,
    SAMPLE_ORGAN_PARTIAL_ENTITY_API_RESPONSE,
    SAMPLE_SECTION_PARTIAL_ENTITY_API_RESPONSE,
    TEST_GET_TSV_ERRORS_PARAMS,
)

CONSTRAINTS_URL_PARAMS = {"match": True, "order": "ancestors"}
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
    def upload(self):
        upload = Upload(directory_path=Path("."))
        upload.app_context = {
            "constraints_url": CONSTRAINTS_URL,
            "entities_url": ENTITIES_URL,
        }
        upload.verbose = False
        upload.globus_token = "test"
        return upload

    def test_bad_payload(self):
        payload = self.upload._construct_constraint_check(BAD_DATASET_SCHEMA_WITH_ANCESTORS)
        assert payload == BAD_DATASET_EXPECTED_PAYLOAD

    def test_good_payload(self):
        payload = self.upload._construct_constraint_check(GOOD_DATASET_SCHEMA_WITH_ANCESTORS)
        assert payload == GOOD_DATASET_EXPECTED_PAYLOAD

    @patch("ingest_validation_tools.upload.requests.post")
    def test_constraints_bad(self, mock_request):
        mock_request.return_value = get_mock_response(False, BAD_DATASET_CONSTRAINTS_RESPONSE)
        self.assertEqual(
            self.upload._constraint_checks(BAD_DATASET_SCHEMA_WITH_ANCESTORS),
            [
                'On row 3, column "source_id", value "test_id_1" fails because of error '
                '"Invalid Ancestor": Invalid ancestor type for TSV type dataset/histology. '
                "Data sent for ancestor test_id_1: sample/organ/rk."
            ],
        )
        mock_request.assert_any_call(
            CONSTRAINTS_URL,
            headers={"Authorization": "Bearer test", "Content-Type": "application/json"},
            data=json.dumps(BAD_DATASET_EXPECTED_PAYLOAD),
            params=CONSTRAINTS_URL_PARAMS,
        )

    @patch("ingest_validation_tools.upload.requests.post")
    def test_constraints_good(self, mock_request):
        mock_request.return_value = get_mock_response(True, SAMPLE_BLOCK_CONSTRAINTS_RESPONSE_GOOD)
        # Shouldn't return anything
        self.upload._constraint_checks(GOOD_DATASET_SCHEMA_WITH_ANCESTORS)
        mock_request.assert_any_call(
            CONSTRAINTS_URL,
            headers={"Authorization": "Bearer test", "Content-Type": "application/json"},
            data=json.dumps(GOOD_DATASET_EXPECTED_PAYLOAD),
            params=CONSTRAINTS_URL_PARAMS,
        )

    @patch("ingest_validation_tools.upload.requests.post")
    @patch("ingest_validation_tools.upload.requests.get")
    def test_expected_ancestor_entities_creation(self, mock_entity_api, mock_cedar_api):
        mock_entity_api.return_value = get_mock_response(
            True, SAMPLE_BLOCK_PARTIAL_ENTITY_API_RESPONSE
        )
        mock_cedar_api.return_value = get_mock_response(
            True, SAMPLE_BLOCK_PARTIAL_CEDAR_RESPONSE_GOOD
        )
        path = Path("./tests/fixtures/sample-block-good.tsv").absolute()
        schema = get_schema_version(path, "ascii", globus_token="test")
        self.upload._get_url_errors(path, schema)
        assert len(schema.ancestor_entities) == 2
        assert schema.ancestor_entities[1].entity_sub_type == Sample.BLOCK.name.lower()
        assert schema.ancestor_entities[0].entity_type == OtherTypes.SAMPLE

    @property
    def entity_api_response_map(self) -> dict[str, bytes]:
        return {
            f"{ENTITIES_URL}HBM233.CGGG.482": SAMPLE_SECTION_PARTIAL_ENTITY_API_RESPONSE,
            f"{ENTITIES_URL}HBM724.ZQKX.379": SAMPLE_BLOCK_PARTIAL_ENTITY_API_RESPONSE,
            f"{ENTITIES_URL}HBM427.JWVV.723": SAMPLE_BLOCK_PARTIAL_ENTITY_API_RESPONSE,
            f"{ENTITIES_URL}HBM733.HSZF.798": SAMPLE_ORGAN_PARTIAL_ENTITY_API_RESPONSE,
            f"{ENTITIES_URL}HBM673.ZRWW.589": SAMPLE_BLOCK_PARTIAL_ENTITY_API_RESPONSE,
        }

    @parameterized.expand(TEST_GET_TSV_ERRORS_PARAMS)
    def test_get_other_tsv_errors(
        self,
        good: bool,
        constraint_checks_response: bytes,
        cedar_response: bytes,
        path: str,
        schema_name: str,
        expected_errors_list: list[list],
    ):
        with patch("ingest_validation_tools.upload.requests.post") as mock_constraints_response:
            with patch("ingest_validation_tools.upload.cedar_validation_call") as mock_cedar_call:
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
                        for report_type in [ReportType.JSON, ReportType.STR]:
                            errors = get_tsv_errors(
                                Path(path).absolute(),
                                schema_name,
                                globus_token="test",
                                app_context={
                                    "entities_url": ENTITIES_URL,
                                    "constraints_url": CONSTRAINTS_URL,
                                },
                                report_type=report_type,
                            )
                            assert errors in expected_errors_list

    def test_entity_type_info(self):
        good_section_entity = EntityTypeInfo(entity_type=Sample.SECTION)
        data = good_section_entity.format_constraint_check_data()
        assert data == {"entity_type": "sample", "sub_type": ["section"], "sub_type_val": None}
        good_organ_entity_fullname = EntityTypeInfo(
            entity_type=Sample.ORGAN, entity_sub_type_val="BD"
        )
        data = good_organ_entity_fullname.format_constraint_check_data()
        assert data == {"entity_type": "sample", "sub_type": ["organ"], "sub_type_val": ["BD"]}
        good_organ_entity = EntityTypeInfo(
            entity_type=OtherTypes.SAMPLE, entity_sub_type=Sample.ORGAN, entity_sub_type_val="BD"
        )
        data = good_organ_entity.format_constraint_check_data()
        assert data == {"entity_type": "sample", "sub_type": ["organ"], "sub_type_val": ["BD"]}

        dataset_entity = EntityTypeInfo(
            entity_type=DatasetType.DATASET, entity_sub_type="light sheet"
        )
        data = dataset_entity.format_constraint_check_data()
        assert data == {
            "entity_type": "dataset",
            "sub_type": ["light sheet"],
            "sub_type_val": None,
        }
        # Samples must have sub_type
        with self.assertRaises(Exception):
            EntityTypeInfo(entity_type=OtherTypes.SAMPLE)
        # Organs must have sub_type_val
        with self.assertRaises(Exception):
            EntityTypeInfo(entity_type=Sample.ORGAN)

    def test_contributors_contact(self):
        for path, error in [
            (Path("./tests/fixtures/contributors_good.tsv"), {}),
            (
                Path("./tests/fixtures/contributors_bad.tsv"),
                {Path("./tests/fixtures/contributors_bad.tsv"): "No primary contact."},
            ),
        ]:
            upload = Upload(
                directory_path=Path("."),
                tsv_paths=[Path("./tests/fixtures/validated-histology-metadata.tsv")],
            )
            for schema in upload.dataset_metadata.values():
                upload._get_supporting_metadata_schemas(schema, path)
            assert upload.errors.upload_metadata.value == error

    def test_for_empty_columns(self):
        upload = Upload(
            directory_path=Path("."),
            tsv_paths=[Path("./tests/fixtures/validated-histology-metadata.tsv")],
        )
        path = Path("./tests/fixtures/contributors_bad.tsv")
        upload.validate_metadata({path: SchemaVersion("contributors")})
        assert upload.errors.upload_metadata.value == {path: "Empty columns: 5, 12"}


# if __name__ == "__main__":
#     suite = unittest.TestLoader().loadTestsFromTestCase(TestSingleTsv)
#     suite.debug()
