import glob
import json
import re
import unittest
from pathlib import Path
from pprint import pformat
from unittest.mock import patch

from deepdiff import DeepDiff, Delta

from ingest_validation_tools.error_report import ErrorReport
from ingest_validation_tools.schema_loader import PreflightError, SchemaVersion
from ingest_validation_tools.upload import Upload
from tests.fixtures import (
    SCATACSEQ_BOTH_VERSIONS_VALID,
    SCATACSEQ_HIGHER_VERSION_VALID,
    SCATACSEQ_LOWER_VERSION_VALID,
    SCATACSEQ_NEITHER_VERSION_VALID,
)

CONSTRAINTS_URL = "http://constraints_test/"
ENTITIES_URL = "http://entities_test/"

SHARED_OPTS = {
    "encoding": "ascii",
}
DATASET_EXAMPLES_OPTS: dict = SHARED_OPTS | {
    "dataset_ignore_globs": ["ignore-*.tsv", ".*"],
    "upload_ignore_globs": ["drv_ignore_*"],
}
DATASET_IEC_EXAMPLES_OPTS = SHARED_OPTS | {
    "dataset_ignore_globs": ["metadata.tsv"],
    "upload_ignore_globs": ["*"],
}
PLUGIN_EXAMPLES_OPTS = DATASET_EXAMPLES_OPTS | {
    "plugin_directory": "../ingest-validation-tests/src/ingest_validation_tests/",
    "run_plugins": True,
    "offline_only": True,
}


class MockException(Exception):
    def __init__(self, error):
        super().__init__(error)


def mutate_upload_errors_with_fixtures(upload: Upload, test_dir: str) -> Upload:
    """
    Validation behavior requiring API calls is mocked. Insert fixture data into
    upload.errors ErrorDict.
    ErrorDict fields requiring updates from fixtures:
        Spreadsheet Validator Errors (ErrorDict.metadata_valdiation_api)
        URL Check Errors (ErrorDict.metadata_url_errors)
    """
    url_errors_field_name = upload.errors.metadata_url_errors.display_name
    api_errors_field_name = upload.errors.metadata_validation_api.display_name
    for tsv_path, schema in upload.dataset_metadata.items():
        fixtures = get_online_check_fixtures(schema.schema_name, test_dir)
        url_errors = fixtures.get(url_errors_field_name, {})
        if url_errors:
            upload.errors.metadata_url_errors[tsv_path] = url_errors
        api_errors = fixtures.get(api_errors_field_name, {})
        if api_errors:
            upload.errors.metadata_validation_api[tsv_path] = api_errors
        antibodies_paths = set()
        contributors_paths = set()
        for row in schema.rows:
            if antibodies_path := row.get("antibodies_path"):
                antibodies_paths.add(antibodies_path)
            if contributors_path := row.get("contributors_path"):
                contributors_paths.add(contributors_path)
        for other_type, paths in {
            "antibodies": antibodies_paths,
            "contributors": contributors_paths,
        }.items():
            for path in paths:
                full_path = upload.directory_path / path
                other_fixtures = get_online_check_fixtures(other_type, test_dir)
                other_url_errors = other_fixtures.get(url_errors_field_name, {})
                if other_url_errors:
                    upload.errors.metadata_url_errors[full_path] = other_url_errors
                other_api_errors = other_fixtures.get(api_errors_field_name, {})
                if other_api_errors:
                    upload.errors.metadata_validation_api[full_path] = other_api_errors
    return upload


def dataset_test(
    test_dir: str,
    dataset_opts: dict,
    verbose: bool = False,
    globus_token: str = "",
    offline: bool = False,
):
    dataset_opts = dataset_opts | {"verbose": verbose}
    print(f"Testing {test_dir}...")
    if offline:
        upload = TestDatasetExamples.prep_offline_upload(test_dir, dataset_opts)
    else:
        upload = Upload(Path(f"{test_dir}/upload"), globus_token=globus_token, **dataset_opts)
    report = ErrorReport(upload)
    with open(f"{test_dir}/README.json", "r") as f:
        diff_test(test_dir, json.load(f), check_report(report), verbose=verbose)
    if "PreflightError" in report.as_md():
        raise MockException(
            f"Error report for {test_dir} contains PreflightError, do not make assertions about calls."
        )


def check_report(report: ErrorReport) -> ErrorReport:
    no_token_regex = re.compile("No token")
    for line in report.as_md().splitlines(keepends=True):
        no_token_regex_match = no_token_regex.search(line)
        if no_token_regex_match:
            raise Exception("API token required to update data.")
    return report


def diff_test(
    test_dir: str, readme: dict, report: ErrorReport, verbose: bool = True, dry_run: bool = False
) -> dict:
    if report.errors:
        diff = DeepDiff(
            readme, report.errors, ignore_order=True, report_repetition=True, verbose_level=2
        )
    else:
        diff = DeepDiff(
            readme,
            report.info,
            ignore_order=True,
            report_repetition=True,
            verbose_level=2,
            exclude_paths=["root['Time']", "root['Git version']"],
        )
    delta = Delta(diff, bidirectional=True)
    flat_rows = delta.to_flat_rows()
    simple_diff = []
    for change in flat_rows:
        entry = {}
        entry["key"] = change.path
        entry["old"] = change.old_value
        entry["new"] = change.value
        simple_diff.append(entry)
    msg = ""
    if verbose:
        msg = f"""
                DIFF FOUND:
                {pformat(simple_diff, indent=2)}
                """
        if dry_run:
            msg = f"""
                {msg}

                If new version is correct, overwrite previous README.json and fixtures.json files by running:
                    env PYTHONPATH=src:$PYTHONPATH python -m tests.manual.update_test_data -t {test_dir} -g <globus_token>

                For help / other options:
                    env PYTHONPATH=src:$PYTHONPATH python -m tests.manual.update_test_data --help
                """
    elif dry_run:
        msg = f"""
                FAILED diff_test: {test_dir}. Run for more detailed output:
                    env PYTHONPATH=src:$PYTHONPATH python -m tests.manual.update_test_data -t {test_dir} --globus_token "" --offline_test --dry_run --verbose
                """
    assert not diff, msg
    print(f"PASSED diff_test: {test_dir}")
    return diff


def _open_and_read_fixtures_file(path: str) -> dict:
    try:
        with open(Path(path) / "fixtures.json") as f:
            opened = json.load(f)
            f.close()
    except json.JSONDecodeError:
        return {}
    return opened


def get_online_check_fixtures(schema_name: str, dir_path: str) -> dict:
    fixture = _open_and_read_fixtures_file(dir_path)
    value = fixture.get("validation", {}).get(schema_name, {})
    if value is None:
        return {}
    return value


def assaytype_side_effect(path: str, row: dict, *args, **kwargs):
    del args, kwargs
    response_dict = _open_and_read_fixtures_file(path)
    dataset_type = row.get("assay_type") if row.get("assay_type") else row.get("dataset_type")
    return response_dict.get("assaytype", {}).get(dataset_type)


class TestExamples(unittest.TestCase):
    dataset_test_dirs = []
    errors = []

    def setUp(self):
        super().setUp()
        self.get_paths()

    def tearDown(self):
        error_lines = "\n".join([str(error) for error in self.errors])
        errors = " ".join([str(error) for error in self.errors])
        self.assertEqual(
            [],
            self.errors,
            f"""

                -------ERRORS-------
                {error_lines}

                Run for more detailed output:
                    env PYTHONPATH=src:$PYTHONPATH python -m tests.manual.update_test_data -t {errors} --verbose --globus_token "" --offline_test --dry_run
                """,
        )

    def get_paths(self):
        self.dataset_paths = {}
        for test_dir in self.dataset_test_dirs:
            metadata_paths = [path for path in Path(f"{test_dir}/upload").glob("*metadata.tsv")]
            self.dataset_paths[test_dir] = metadata_paths

    def test_validate_dataset_examples(self, verbose: bool = False):
        for test_dir in self.dataset_paths.keys():
            with self.subTest(test_dir=test_dir):
                if "dataset-examples" in test_dir:
                    opts = DATASET_EXAMPLES_OPTS
                elif "dataset-iec-examples" in test_dir:
                    opts = DATASET_IEC_EXAMPLES_OPTS
                elif "plugin-tests" in test_dir:
                    opts = PLUGIN_EXAMPLES_OPTS
                else:
                    opts = {}
                with patch("ingest_validation_tools.validation_utils.get_assaytype_data"):
                    with patch("ingest_validation_tools.upload.Upload._get_url_errors"):
                        with patch(
                            "ingest_validation_tools.local_validation.check_factory.cache_path",
                            Path(__file__).parent / "fixtures/url-status-cache.json",
                        ):
                            try:
                                dataset_test(
                                    test_dir,
                                    opts,
                                    verbose=verbose,
                                    offline=True,
                                )
                            except MockException as e:
                                print(e)
                                continue
                            except AssertionError as e:
                                print(e)
                                self.errors.append(test_dir)
                                continue

    @staticmethod
    def prep_offline_upload(test_dir: str, opts: dict) -> Upload:
        with patch(
            "ingest_validation_tools.validation_utils.get_assaytype_data",
            side_effect=lambda row, ingest_url, globus_token: assaytype_side_effect(
                test_dir, row, ingest_url, globus_token
            ),
        ):
            with patch("ingest_validation_tools.validation_utils.get_entity_api_data"):
                with patch("ingest_validation_tools.upload.Upload._online_checks"):
                    upload = Upload(Path(f"{test_dir}/upload"), **opts)
                    upload.get_errors()
                    upload = mutate_upload_errors_with_fixtures(upload, test_dir)
                    upload.get_info()
                    return upload


class TestDatasetExamples(TestExamples):
    dataset_test_dirs = [
        test_dir
        for test_dir in [
            *glob.glob("examples/dataset-examples/**"),
            *glob.glob("examples/dataset-iec-examples/**"),
        ]
        if Path(test_dir).is_dir()
    ]

    def prep_dir_schema_upload(self, test_dir: str, opts: dict, patch_data: dict) -> Upload:
        with patch(
            "ingest_validation_tools.validation_utils.get_assaytype_data",
            side_effect=lambda row, ingest_url, globus_token: assaytype_side_effect(
                test_dir, row, ingest_url, globus_token
            ),
        ):
            with patch(
                "ingest_validation_tools.validation_utils.get_possible_directory_schemas",
            ) as dir_schemas_func_patch:
                with patch("ingest_validation_tools.upload.Upload._online_checks"):
                    dir_schemas_func_patch.return_value = patch_data
                    upload = Upload(Path(f"{test_dir}/upload"), **opts)
                    upload.get_errors()
                    upload = mutate_upload_errors_with_fixtures(upload, test_dir)
                    dir_schemas_func_patch.assert_called()
                    return upload

    def test_data_dir_versions_highest_version(self):
        test_dirs = [
            "examples/dataset-examples/bad-scatacseq-data",
            "examples/dataset-examples/good-scatacseq-metadata-v0",
        ]
        for test_dir in test_dirs:
            upload = self.prep_dir_schema_upload(
                test_dir, DATASET_EXAMPLES_OPTS, SCATACSEQ_HIGHER_VERSION_VALID
            )
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

    def test_data_dir_versions_lower_version(self):
        test_dirs = [
            "examples/dataset-examples/bad-scatacseq-data",
            "examples/dataset-examples/good-scatacseq-metadata-v0",
        ]
        test_dirs = []
        for test_dir in test_dirs:
            upload = self.prep_dir_schema_upload(
                test_dir, DATASET_EXAMPLES_OPTS, SCATACSEQ_LOWER_VERSION_VALID
            )
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
                self.assertEqual(dir_schema_version, "test-schema-v1.0")

    def test_data_dir_versions_both_versions(self):
        test_dirs = [
            "examples/dataset-examples/bad-scatacseq-data",
            "examples/dataset-examples/good-scatacseq-metadata-v0",
        ]
        test_dirs = []
        for test_dir in test_dirs:
            upload = self.prep_dir_schema_upload(
                test_dir, DATASET_EXAMPLES_OPTS, SCATACSEQ_BOTH_VERSIONS_VALID
            )
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

    def test_data_dir_versions_neither_version(self):
        test_dirs = [
            "examples/dataset-examples/bad-scatacseq-data",
            "examples/dataset-examples/good-scatacseq-metadata-v0",
        ]
        test_dirs = []
        for test_dir in test_dirs:
            upload = self.prep_dir_schema_upload(
                test_dir, DATASET_EXAMPLES_OPTS, SCATACSEQ_NEITHER_VERSION_VALID
            )
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
                self.assertEqual(dir_schema_version, None)

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
            "ingest_validation_tools.validation_utils.get_assaytype_data",
        ):
            with patch("ingest_validation_tools.upload.Upload._online_checks"):
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
                        SchemaVersion(
                            schema_name="visium-no-probes", contains=["histology", "rnaseq"]
                        ),
                    )

    def test_counts(self):
        test_dirs = {
            "examples/dataset-examples/bad-cedar-assay-histology": {
                "Spreadsheet Validator Errors": 2,
                "URL Check Errors": 1,
                "No References": 1,
                "Plugins Skipped": True,
            },
            "examples/dataset-examples/bad-cedar-rnaseq-contributors": {
                "Antibodies/Contributors Errors": 1,
                "Plugins Skipped": True,
            },
            "examples/dataset-examples/good-scatacseq-metadata-v0": {},
            "examples/dataset-examples/bad-mixed": {
                "Preflight Errors": "Found multiple dataset types in upload: CODEX, SNARE-seq2."
            },
        }
        with patch(
            "ingest_validation_tools.local_validation.check_factory.cache_path",
            Path(__file__).parent / "fixtures/url-status-cache.json",
        ):
            for test_dir, expected_counts in test_dirs.items():
                upload = self.prep_offline_upload(test_dir, DATASET_EXAMPLES_OPTS)
                report = ErrorReport(upload)
                self.assertEqual(report.counts, expected_counts)


# if __name__ == "__main__":
#     suite = unittest.TestLoader().loadTestsFromTestCase(TestDatasetExamples)
#     suite.debug()
