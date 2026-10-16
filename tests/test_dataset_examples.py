import unittest
from pathlib import Path
from unittest.mock import patch

from vcr.unittest import VCRTestCase

from ingest_validation_tools.error_report import ErrorReport
from ingest_validation_tools.schema_loader import PreflightError, SchemaVersion
from ingest_validation_tools.upload import Upload
from tests.fixtures import SCATACSEQ_BOTH_VERSIONS_VALID, SCATACSEQ_HIGHER_VERSION_VALID
from tests.vcr_utils import (
    DATASET_EXAMPLES_OPTS,
    get_example_paths,
    test_dataset_examples,
)


class TestExamples(unittest.TestCase):
    """
    Test all directories in examples/.
    """

    errors = []

    @property
    def dataset_test_dirs(self):
        return get_example_paths()

    def test_dataset_examples(self):
        test_dataset_examples(self.dataset_test_dirs)


class TestUploads(VCRTestCase):

    def before_record_request(self, request: Request) -> Request:
        """
        Strip headers.
        """
        request.headers = None
        return request

    def before_record_response(self, response: dict) -> dict:
        """
        Strip headers, raise if Unauthorized, 500, No token errors.
        """
        response["headers"] = {}
        return response

    # TODO: needs easier way to update w/ globus token
    def _get_vcr(self, **kwargs):
        kwargs["before_record_request"] = self.before_record_request
        kwargs["before_record_response"] = self.before_record_response
        myvcr = super(TestUploads, self)._get_vcr(**kwargs)
        return myvcr

    def test_data_dir_versions_highest_version(self):
        test_dirs = [
            Path("examples/dataset-examples/bad-scatacseq-data"),
            Path("examples/dataset-examples/good-scatacseq-metadata-v0"),
        ]
        for test_dir in test_dirs:
            with patch(
                "ingest_validation_tools.validation_utils.get_possible_directory_schemas",
            ) as dir_schemas_func_patch:
                dir_schemas_func_patch.return_value = SCATACSEQ_HIGHER_VERSION_VALID
                upload = Upload(Path(test_dir / "upload"), **DATASET_EXAMPLES_OPTS)
                upload.get_errors()
                dir_schemas_func_patch.assert_called()
            info = upload.get_info()
            if info is None:
                raise Exception("Info should not be none")
            for path in upload.dataset_metadata.keys():
                dir_schema_version = (
                    info.as_dict()
                    .get("TSVs", {})
                    .get(Path(path).name, {})
                    .get("Directory schema version")
                )
                self.assertEqual(dir_schema_version, "test-schema-v0.1")

    def test_data_dir_versions_both_versions(self):
        test_dirs = [
            Path("examples/dataset-examples/bad-scatacseq-data"),
            Path("examples/dataset-examples/good-scatacseq-metadata-v0"),
        ]
        for test_dir in test_dirs:
            with patch(
                "ingest_validation_tools.validation_utils.get_possible_directory_schemas",
            ) as dir_schemas_func_patch:
                dir_schemas_func_patch.return_value = SCATACSEQ_BOTH_VERSIONS_VALID
                upload = Upload(Path(test_dir / "upload"), **DATASET_EXAMPLES_OPTS)
                upload.get_errors()
                dir_schemas_func_patch.assert_called()
            info = upload.get_info()
            if info is None:
                raise Exception("Info should not be none")
            for path in upload.dataset_metadata.keys():
                dir_schema_version = (
                    info.as_dict()
                    .get("TSVs", {})
                    .get(Path(path).name, {})
                    .get("Directory schema version")
                )
                self.assertEqual(dir_schema_version, "test-schema-v0.1")

    def get_schema_side_effect(
        self, tsv_path, encoding, entities_url, ingest_url, globus_token, directory_path
    ):
        del encoding, entities_url, ingest_url, globus_token, directory_path
        schema_map = {
            "repeated_parent_fake_path_1": SchemaVersion(
                schema_name="visium-no-probes", contains=["histology", "rnaseq"]
            ),
            "repeated_parent_fake_path_2": SchemaVersion(
                schema_name="visium-no-probes", contains=["histology", "rnaseq"]
            ),
            "unique_parent_fake_path_1": SchemaVersion(
                schema_name="visium-no-probes", contains=["histology", "rnaseq"]
            ),
            "unique_parent_fake_path_2": SchemaVersion(schema_name="histology"),
        }
        return schema_map.get(str(tsv_path))

    def test_bad_multi_assay_parents(self):
        with patch(
            "ingest_validation_tools.upload.get_schema_version",
            side_effect=lambda tsv_path, encoding, entities_url, ingest_url, globus_token, directory_path: self.get_schema_side_effect(
                tsv_path, encoding, entities_url, ingest_url, globus_token, directory_path
            ),
        ):
            bad_upload = Upload(
                Path("test_path"),
                tsv_paths=["repeated_parent_fake_path_1", "repeated_parent_fake_path_2"],
                **DATASET_EXAMPLES_OPTS,
            )
            with self.assertRaises(PreflightError):
                bad_upload.multi_parent
            good_upload = Upload(
                Path("test_path"),
                tsv_paths=["unique_parent_fake_path_1", "unique_parent_fake_path_2"],
                **DATASET_EXAMPLES_OPTS,
            )
            self.assertEqual(
                good_upload.multi_parent,
                SchemaVersion(schema_name="visium-no-probes", contains=["histology", "rnaseq"]),
            )

    def test_counts(self):
        test_dirs = {
            Path("examples/dataset-examples/bad-cedar-assay-histology"): {
                "Spreadsheet Validator Errors": 2,
                "URL Check Errors": 1,
                "No References": 1,
                "Plugins Skipped": True,
            },
            Path("examples/dataset-examples/bad-cedar-rnaseq-contributors"): {
                "Antibodies/Contributors Errors": 1,
                "Plugins Skipped": True,
            },
            Path("examples/dataset-examples/good-scatacseq-metadata-v0"): {},
            Path("examples/dataset-examples/bad-mixed"): {
                "Preflight Errors": "Found multiple dataset types in upload: CODEX, SNARE-seq2."
            },
        }
        for test_dir, expected_counts in test_dirs.items():
            upload = Upload(Path(test_dir / "upload"), **DATASET_EXAMPLES_OPTS)
            report = ErrorReport(upload)
            self.assertEqual(report.counts, expected_counts)

    # TODO: fix; not migrated to VCR paradigm
    # def test_data_dir_versions_lower_version(self):
    #     test_dirs = [
    #         Path("examples/dataset-examples/bad-scatacseq-data"),
    #         Path("examples/dataset-examples/good-scatacseq-metadata-v0"),
    #     ]
    #     for test_dir in test_dirs:
    #         upload = self.prep_dir_schema_upload(
    #             test_dir, DATASET_EXAMPLES_OPTS, SCATACSEQ_LOWER_VERSION_VALID
    #         )
    #         info = upload.get_info()
    #         if info is None:
    #             raise Exception("Info should not be none")
    #         for path in upload.dataset_metadata.keys():
    #             dir_schema_version = (
    #                 info.as_dict()
    #                 .get("TSVs", {})
    #                 .get(Path(path).name, {})
    #                 .get("Directory schema version")
    #             )
    #             self.assertEqual(dir_schema_version, "test-schema-v1.0")
    # TODO: fix
    # def test_data_dir_versions_neither_version(self):
    #     test_dirs = [
    #         Path("examples/dataset-examples/bad-scatacseq-data"),
    #         Path("examples/dataset-examples/good-scatacseq-metadata-v0"),
    #     ]
    #     for test_dir in test_dirs:
    #         upload = self.prep_dir_schema_upload(
    #             test_dir, DATASET_EXAMPLES_OPTS, SCATACSEQ_NEITHER_VERSION_VALID
    #         )
    #         info = upload.get_info()
    #         if info is None:
    #             raise Exception("Info should not be none")
    #         for path in upload.dataset_metadata.keys():
    #             dir_schema_version = (
    #                 info.as_dict()
    #                 .get("TSVs", {})
    #                 .get(Path(path).name, {})
    #                 .get("Directory schema version")
    #             )
    #             self.assertEqual(dir_schema_version, None)
