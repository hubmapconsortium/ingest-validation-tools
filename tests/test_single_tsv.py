import argparse
import json
import sys
import unittest
from pathlib import Path

from parameterized import parameterized
from vcr.request import Request
from vcr.unittest import VCRTestCase

from ingest_validation_tools.enums import DatasetType, OtherTypes, Sample
from ingest_validation_tools.local_validation.table_validator import ReportType
from ingest_validation_tools.schema_loader import EntityTypeInfo, SchemaVersion
from ingest_validation_tools.upload import Upload
from ingest_validation_tools.validation_utils import get_schema_version, get_tsv_errors
from tests.fixtures.fixtures import (
    BAD_DATASET_EXPECTED_PAYLOAD,
    BAD_DATASET_SCHEMA_WITH_ANCESTORS,
    GOOD_DATASET_EXPECTED_PAYLOAD,
    GOOD_DATASET_SCHEMA_WITH_ANCESTORS,
    TEST_GET_TSV_ERRORS_PARAMS,
)
from tests.manual.updaters import raise_or_print_fatal_errors
from tests.utils import default_before_record_request, validation_matcher

CONSTRAINTS_URL_PARAMS = {"match": True, "order": "ancestors"}
SENNET_APP_CONTEXT = {
    "entities_url": "https://entity.api.sennetconsortium.org/entities",
    "constraints_url": "https://entity.api.sennetconsortium.org/constraints",
}

SENNET_TOKEN = "test_sennet_token"
HUBMAP_TOKEN = "test_hubmap_token"


class TestSingleTsv(VCRTestCase):

    def before_record_response(self, response: dict) -> dict:
        """
        Strip headers, raise if Unauthorized, 500, No token errors.
        """
        response["headers"] = {}
        raise_or_print_fatal_errors(response["body"]["string"].decode("utf-8"))
        return response

    def _get_vcr(self, **kwargs):
        kwargs["before_record_request"] = default_before_record_request
        kwargs["before_record_response"] = self.before_record_response
        kwargs["cassette_library_dir"] = "tests/fixtures/cassettes"
        myvcr = super(TestSingleTsv, self)._get_vcr(**kwargs)
        myvcr.register_matcher("validation_matcher", validation_matcher)
        myvcr.match_on = ["validation_matcher"]
        return myvcr

    @property
    def sennet_upload(self):
        upload = Upload(directory_path=Path("."))
        upload.verbose = False
        upload.app_context = SENNET_APP_CONTEXT
        upload.globus_token = SENNET_TOKEN
        return upload

    def test_bad_payload(self):
        payload = self.sennet_upload._construct_constraint_check(BAD_DATASET_SCHEMA_WITH_ANCESTORS)
        assert payload == BAD_DATASET_EXPECTED_PAYLOAD

    def test_good_payload(self):
        payload = self.sennet_upload._construct_constraint_check(
            GOOD_DATASET_SCHEMA_WITH_ANCESTORS
        )
        assert payload == GOOD_DATASET_EXPECTED_PAYLOAD

    def test_constraints_bad(self):
        self.assertEqual(
            self.sennet_upload._constraint_checks(BAD_DATASET_SCHEMA_WITH_ANCESTORS),
            [
                'On row 3, column "source_id", value "test_id_1" fails because of error '
                '"Invalid Ancestor": Invalid ancestor type for TSV type dataset/histology. '
                "Data sent for ancestor test_id_1: sample/organ/rk."
            ],
        )
        # This tests the existing cassette, only useful when creating a new version
        self.assertEqual(len(self.cassette), 1)
        self.assertEqual(
            self.cassette.requests[0].body,
            json.dumps(BAD_DATASET_EXPECTED_PAYLOAD).encode("utf-8"),
        )
        self.assertEqual(
            self.cassette.requests[0].uri,
            "https://entity.api.sennetconsortium.org/constraints?match=True&order=ancestors",
        )

    def test_constraints_good(self):
        assert self.sennet_upload._constraint_checks(GOOD_DATASET_SCHEMA_WITH_ANCESTORS) == None
        # This tests the existing cassette, only useful when creating a new version
        self.assertEqual(len(self.cassette), 1)
        self.assertEqual(
            self.cassette.requests[0].body,
            json.dumps(GOOD_DATASET_EXPECTED_PAYLOAD).encode("utf-8"),
        )
        self.assertEqual(
            self.cassette.requests[0].uri,
            "https://entity.api.sennetconsortium.org/constraints?match=True&order=ancestors",
        )

    def test_expected_ancestor_entities_creation(self):
        path = Path("./tests/fixtures/sample-block-good.tsv").absolute()
        schema = get_schema_version(
            path,
            "ascii",
            globus_token=SENNET_TOKEN,
            entity_url="https://entity.api.sennetconsortium.org/entities/",
        )
        self.sennet_upload._get_url_errors(path, schema)
        assert len(schema.ancestor_entities) == 4
        assert schema.ancestor_entities[1].entity_sub_type == Sample.BLOCK.name.lower()
        assert schema.ancestor_entities[0].entity_type == OtherTypes.SAMPLE
        assert schema.ancestor_entities[3].entity_sub_type == Sample.BLOCK.name.lower()
        assert schema.ancestor_entities[2].entity_type == OtherTypes.SAMPLE

    def test_get_other_tsv_errors_good(self):
        for report_type in [ReportType.JSON, ReportType.STR]:
            errors = get_tsv_errors(
                Path("./tests/fixtures/sample-block-good.tsv"),
                "sample-block",
                globus_token=SENNET_TOKEN,
                report_type=report_type,
                app_context=SENNET_APP_CONTEXT,
            )
            assert errors in [[], []], f"Unexpected errors found! {errors}"

    @parameterized.expand(TEST_GET_TSV_ERRORS_PARAMS)
    def test_get_other_tsv_errors_bad(
        self,
        path: str,
        schema_name: str,
        expected_errors_list: list[list],
    ):
        for report_type in [ReportType.JSON, ReportType.STR]:
            errors = get_tsv_errors(
                Path(path),
                schema_name,
                globus_token=HUBMAP_TOKEN,
                report_type=report_type,
            )
            assert errors in expected_errors_list, f"{errors} not in {expected_errors_list}"

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
        upload = Upload(directory_path=Path("."))
        path = Path("./tests/fixtures/contributors_bad.tsv")
        upload.validate_metadata({path: SchemaVersion("contributors")})
        assert upload.errors.upload_metadata.value == {path: "Empty columns: 5"}


if __name__ == "__main__":
    """
    Example usage:
        python tests/test_single_tsv.py -ht <hubmap_globus_token>
        python tests/test_single_tsv.py -st <sennet_globus_token> TestSingleTsv.test_expected_ancestor_entities_creation
    """
    parser = argparse.ArgumentParser(
        description="Pass SenNet and/or HuBMAP Globus tokens to update fixture cassettes (must delete previous cassette) from tests/fixtures/cassettes"
    )
    parser.add_argument("-st", "--sennet_token")
    parser.add_argument("-ht", "--hubmap_token")
    parser.add_argument("unittest_args", nargs="*")

    args = parser.parse_args()

    if args.sennet_token:
        SENNET_TOKEN = args.sennet_token
    if args.hubmap_token:
        HUBMAP_TOKEN = args.hubmap_token
    sys.argv[1:] = args.unittest_args
    unittest.main()
