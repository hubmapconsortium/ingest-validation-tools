import argparse
import sys
import unittest
from datetime import datetime
from glob import glob
from pathlib import Path
from unittest.mock import patch

from vcr.request import Request
from vcr.unittest import VCRTestCase

from ingest_validation_tools.directory_validator import (
    DirectoryValidationErrors,
    validate_directory,
)
from ingest_validation_tools.error_report import ErrorReport, InfoDict
from ingest_validation_tools.schema_loader import PreflightError, SchemaVersion
from ingest_validation_tools.upload import Upload
from ingest_validation_tools.validation_utils import get_data_dir_errors
from tests.fixtures.fixtures import (
    SCATACSEQ_BOTH_VERSIONS_VALID,
    SCATACSEQ_HIGHER_VERSION_VALID,
    SCATACSEQ_LOWER_VERSION_VALID,
    SCATACSEQ_NEITHER_VERSION_VALID,
)
from tests.manual.updaters import remove_minor_version
from tests.utils import (
    DATASET_EXAMPLES_OPTS,
    default_before_record_request,
    default_before_record_response,
    get_example_paths,
    prepare_change_report,
    test_dataset_examples,
)

TOKEN = "offline_test_token"


def get_dataset_example_opts():
    return DATASET_EXAMPLES_OPTS | {"globus_token": TOKEN}


class TestExamples(unittest.TestCase):
    """
    Test all directories in examples/.
    """

    errors = []

    @property
    def dataset_test_dirs(self):
        return get_example_paths()

    def test_dataset_examples(self):
        errors = test_dataset_examples(self.dataset_test_dirs, globus_token=TOKEN)
        assert not errors, "\n".join(prepare_change_report(errors))


class TestUploads(VCRTestCase):

    def before_record_request(self, request: Request) -> Request:
        return default_before_record_request(request)

    def before_record_response(self, response: dict) -> dict:
        return default_before_record_response(response)

    def _get_vcr(self, **kwargs):
        kwargs["before_record_request"] = self.before_record_request
        kwargs["before_record_response"] = self.before_record_response
        kwargs["cassette_library_dir"] = "tests/fixtures/cassettes"
        myvcr = super(TestUploads, self)._get_vcr(**kwargs)
        return myvcr

    def test_data_dir_versions_highest_version(self):
        test_dirs = {
            Path("examples/dataset-examples/bad-scatacseq-data"): {
                "raises": (True, True),
                "expected_errors": {
                    "test-schema-v0.1": {"Required but missing": [".*\\.fastq\\.gz"]}
                },
            },
            Path("examples/dataset-examples/good-scatacseq-metadata-v0"): {
                "raises": (True, False),
                "expected_errors": {"test-schema-v0.1": {}},
            },
        }
        for test_dir, data in test_dirs.items():
            for i, (_, schema) in enumerate(SCATACSEQ_HIGHER_VERSION_VALID.items()):
                if data["raises"][i]:
                    with self.assertRaises(DirectoryValidationErrors):
                        validate_directory([test_dir], schema["files"])
                else:
                    validate_directory([test_dir], schema["files"])
            with patch(
                "ingest_validation_tools.validation_utils.get_possible_directory_schemas",
            ) as dir_schemas_func_patch:
                dir_schemas_func_patch.return_value = SCATACSEQ_HIGHER_VERSION_VALID
                errors = get_data_dir_errors("test-schema-v0", Path("."), test_dir)
                assert errors == data["expected_errors"]

    def test_data_dir_versions_lower_version(self):
        test_dir = Path("examples/dataset-examples/good-scatacseq-metadata-v0")
        for schema_name, schema in SCATACSEQ_LOWER_VERSION_VALID.items():
            if schema_name == "test-schema-v0.1":
                with self.assertRaises(DirectoryValidationErrors):
                    validate_directory([test_dir], schema["files"])
            else:
                validate_directory([test_dir], schema["files"])
        with patch(
            "ingest_validation_tools.validation_utils.get_possible_directory_schemas",
        ) as dir_schemas_func_patch:
            dir_schemas_func_patch.return_value = SCATACSEQ_LOWER_VERSION_VALID
            errors = get_data_dir_errors("test-schema-v0", Path("."), test_dir)
            assert errors == {"test-schema-v0.0": {}}

    def test_data_dir_versions_neither_version(self):
        """
        Dir structure does not match either dir schema, report errors for
        highest/most recent version.
        """
        test_dirs = [
            Path("examples/dataset-examples/bad-scatacseq-data"),
            Path("examples/dataset-examples/good-scatacseq-metadata-v0"),
        ]
        for test_dir in test_dirs:
            for _, schema in SCATACSEQ_NEITHER_VERSION_VALID.items():
                with self.assertRaises(DirectoryValidationErrors):
                    validate_directory([test_dir], schema["files"])
        with patch(
            "ingest_validation_tools.validation_utils.get_possible_directory_schemas",
        ) as dir_schemas_func_patch:
            dir_schemas_func_patch.return_value = SCATACSEQ_NEITHER_VERSION_VALID
            errors = get_data_dir_errors("test-schema-v0", Path("."), test_dir)
            errors["test-schema-v0.1"]

    def test_data_dir_versions_both_versions(self):
        test_dir = Path("examples/dataset-examples/good-scatacseq-metadata-v0/upload")
        for _, schema in SCATACSEQ_BOTH_VERSIONS_VALID.items():
            validate_directory([test_dir], schema["files"])
        with patch(
            "ingest_validation_tools.validation_utils.get_possible_directory_schemas",
        ) as dir_schemas_func_patch:
            dir_schemas_func_patch.return_value = SCATACSEQ_BOTH_VERSIONS_VALID
            errors = get_data_dir_errors("test-schema-v0", Path("."), test_dir)
            assert errors == {"test-schema-v0.1": {}}

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
                **get_dataset_example_opts(),
            )
            with self.assertRaises(PreflightError):
                bad_upload.multi_parent
            good_upload = Upload(
                Path("test_path"),
                tsv_paths=["unique_parent_fake_path_1", "unique_parent_fake_path_2"],
                **get_dataset_example_opts(),
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
            upload = Upload(Path(test_dir / "upload"), **get_dataset_example_opts())
            report = ErrorReport(upload)
            self.assertEqual(report.counts, expected_counts)

    def test_info_reporting(self):
        test_dirs = {
            "examples/dataset-examples/bad-cedar-assay-histology": InfoDict(
                time="WILL_CHANGE",
                git="WILL_CHANGE",
                dir="examples/dataset-examples/bad-cedar-assay-histology/upload",
                tsvs={
                    "bad-histology-metadata.tsv": {
                        "Metadata type": "Histology",
                        "Metadata version": "e7475329-9a60-4088-8e34-19a3828e0b3b",
                        "Directory schema version": "histology-v2.*",
                    }
                },
                successful_plugins=[],
            ),
            "examples/dataset-examples/good-scatacseq-metadata-v0": InfoDict(
                time="WILL_CHANGE",
                git="WILL_CHANGE",
                dir="examples/dataset-examples/good-scatacseq-metadata-v0/upload",
                tsvs={
                    "metadata.tsv": {
                        "Metadata type": "scatacseq-v0",
                        "Metadata version": "0",
                        "Directory schema version": "scatacseq-v0.*",
                    }
                },
                successful_plugins=[],
            ),
        }
        for test_dir, test_info in test_dirs.items():
            upload = Upload(Path(f"{test_dir}/upload"), **DATASET_EXAMPLES_OPTS)
            upload.get_errors()
            upload_info = upload.get_info()
            assert upload_info.git
            assert upload_info.time
            assert upload_info.dir == test_info.dir
            for tsv in upload_info.tsvs.keys():
                dir_schema_version = upload_info.tsvs[tsv].get("Directory schema version")
                if dir_schema_version:
                    upload_info.tsvs[tsv]["Directory schema version"] = remove_minor_version(
                        dir_schema_version
                    )
            assert upload_info.tsvs == test_info.tsvs


if __name__ == "__main__":
    """
    Example usage:
        python tests/test_dataset_examples.py -t <hubmap_globus_token>
    """
    parser = argparse.ArgumentParser(
        description="Pass HuBMAP Globus token to update fixture cassettes (must delete previous cassette) from tests/fixtures/cassettes"
    )
    parser.add_argument("-t", "--token")
    parser.add_argument("unittest_args", nargs="*")

    args = parser.parse_args()

    if args.token:
        TOKEN = args.token
    sys.argv[1:] = args.unittest_args
    unittest.main()
