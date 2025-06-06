import difflib
import glob
import json
import re
import unittest
from io import TextIOWrapper
from pathlib import Path
from typing import Dict, Union
from unittest.mock import patch

from ingest_validation_tools.error_report import DictErrorType, ErrorDict, ErrorReport
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
}


class MockException(Exception):
    def __init__(self, error):
        super().__init__(error)


class TokenException(Exception):
    def __init__(self, error: str, clean_report: Union[str, Dict]):
        super().__init__(error)
        self.clean_report = clean_report


def mutate_upload_errors_with_fixtures(upload: Upload, test_dir: str) -> Upload:
    url_errors_field_name = upload.errors.metadata_url_errors.display_name
    api_errors_field_name = upload.errors.metadata_validation_api.display_name
    for tsv_path, schema in upload.effective_tsv_paths.items():
        fixtures = get_online_check_fixtures(schema.schema_name, test_dir)
        url_errors = fixtures.get(url_errors_field_name, {})
        if url_errors:
            upload.errors.metadata_url_errors[tsv_path] = url_errors
        api_errors = fixtures.get(api_errors_field_name, {})
        if api_errors:
            upload.errors.metadata_validation_api[tsv_path] = api_errors
        for other_type, paths in {
            "antibodies": schema.antibodies_paths,
            "contributors": schema.contributors_paths,
        }.items():
            for path in paths:
                other_fixtures = get_online_check_fixtures(other_type, test_dir)
                other_url_errors = other_fixtures.get(url_errors_field_name, {})
                if other_url_errors:
                    upload.errors.metadata_url_errors[path] = other_url_errors
                other_api_errors = other_fixtures.get(api_errors_field_name, {})
                if other_api_errors:
                    upload.errors.metadata_validation_api[path] = other_api_errors
    return upload


def dataset_test(
    test_dir: str,
    dataset_opts: dict,
    verbose: bool = False,
    globus_token: str = "",
    # TODO: do we need both of these params
    offline: bool = False,
    use_online_check_fixtures: bool = False,
    full_diff: bool = False,
):
    dataset_opts = dataset_opts | {"verbose": verbose}
    print(f"Testing {test_dir}...")
    readme = open(f"{test_dir}/README.md", "r")
    if offline:
        upload = TestDatasetExamples.prep_offline_upload(test_dir, dataset_opts)
    else:
        upload = Upload(Path(f"{test_dir}/upload"), globus_token=globus_token, **dataset_opts)
    if use_online_check_fixtures:
        upload = mutate_upload_errors_with_fixtures(upload, test_dir)
    report = ErrorReport(upload)
    diff_test(test_dir, readme, clean_report(report), verbose=verbose, full_diff=full_diff)
    if "PreflightError" in report.as_md():
        raise MockException(
            f"Error report for {test_dir} contains PreflightError, do not make assertions about calls."
        )


def clean_report(report: ErrorReport):
    token_issue = False
    cleaned_report = []
    will_change_regex = re.compile(r"((Time|Git version): )(.*)")
    no_token_regex = re.compile("No token")
    for line in report.as_md().splitlines(keepends=True):
        will_change_match = will_change_regex.search(line)
        if will_change_match:
            line = line.replace(will_change_match.group(3), "WILL_CHANGE")
        no_token_regex_match = no_token_regex.search(line)
        if no_token_regex_match:
            token_issue = True
        line = dev_url_replace(line)
        cleaned_report.append(line)
    if token_issue:
        if report.raw_errors:
            report.raw_errors = get_non_token_errors(report.raw_errors)
            report.errors = report.raw_errors.as_dict()
        cleaned_report = clean_report(report)
        raise TokenException(
            "WARNING: API token required to complete update, not writing, skipping URL Check Errors.",
            "".join(cleaned_report),
        )
    return "".join(cleaned_report)


def get_non_token_errors(errors: ErrorDict) -> ErrorDict:
    new_url_error_val = DictErrorType(
        name=errors.metadata_url_errors.name, display_name=errors.metadata_url_errors.display_name
    )
    for path, error_list in errors.metadata_url_errors.items():
        non_token_url_errors = [error for error in error_list if "No token" not in error]
        if non_token_url_errors:
            new_url_error_val[path] = non_token_url_errors
        if set(error_list) - set(non_token_url_errors):
            print(
                f"WARNING: output about URL errors for {path} is incomplete due to suppressed token errors. Use for testing purposes only."
            )
    errors.metadata_url_errors = new_url_error_val
    return errors


def dev_url_replace(original_str: str):
    dev_regex = re.compile(r"-api.dev")
    new_str = re.sub(dev_regex, ".api", original_str)
    return new_str


def diff_test(
    test_dir: str,
    readme: TextIOWrapper,
    report: str,
    verbose: bool = True,
    full_diff: bool = False,
    env: str = "PROD",
):
    d = difflib.Differ()
    if env == "DEV":
        report = dev_url_replace(report)
    diff = list(d.compare(readme.readlines(), report.splitlines(keepends=True)))
    readme.close()
    ignore_strings = ["Time:", "Git version:", "```"]
    cleaned_diff = [
        line for line in diff if not any(ignore_string in line for ignore_string in ignore_strings)
    ]
    new = "".join([line.strip() for line in cleaned_diff if line.startswith("+ ")])
    removed = "".join([line.strip() for line in cleaned_diff if line.startswith("- ")])
    if full_diff:
        print(
            f"""
              FULL:
              {diff}

              CLEANED:
              {cleaned_diff}
              """
        )
    if verbose:
        msg = f"""
                DIFF ADDED LINES:
                {new}

                DIFF REMOVED LINES:
                {removed}

                If new version is correct, overwrite previous README.md and fixtures.json files by running:
                    env PYTHONPATH=src:$PYTHONPATH python -m tests-manual.update_test_data -t {test_dir} -g <globus_token>

                For help / other options:
                    env PYTHONPATH=src:$PYTHONPATH python -m tests-manual.update_test_data --help
                """
    else:
        msg = f"""
    FAILED diff_test: {test_dir}. Run for more detailed output:
        env PYTHONPATH=src:$PYTHONPATH python -m tests-manual.update_test_data -t {test_dir} --globus_token "" --manual_test --dry_run --verbose
    """
    assert not new and not removed, msg
    print(f"PASSED diff_test: {test_dir}")


def _open_and_read_fixtures_file(path: str) -> Dict:
    try:
        with open(Path(path) / "fixtures.json") as f:
            opened = json.load(f)
            f.close()
    except json.JSONDecodeError:
        return {}
    return opened


def get_online_check_fixtures(schema_name: str, dir_path: str) -> Dict:
    fixture = _open_and_read_fixtures_file(dir_path)
    value = fixture.get("validation", {}).get(schema_name, {})
    if value is None:
        return {}
    return value


def assaytype_side_effect(path: str, row: Dict, *args, **kwargs):
    del args, kwargs
    response_dict = _open_and_read_fixtures_file(path)
    dataset_type = row.get("assay_type") if row.get("assay_type") else row.get("dataset_type")
    return response_dict.get("assaytype", {}).get(dataset_type)


class TestDatasetExamples(unittest.TestCase):
    dataset_test_dirs = [
        test_dir
        for test_dir in [
            *glob.glob("examples/dataset-examples/**"),
            *glob.glob("examples/dataset-iec-examples/**"),
        ]
        if Path(test_dir).is_dir()
    ]
    errors = []

    def setUp(self):
        super().setUp()
        self.get_paths()

    def tearDown(self):
        error_lines = "\n".join([str(error) for error in self.errors])
        errors = " ".join([str(error) for error in self.errors])
        try:
            self.assertEqual([], self.errors)
        except AssertionError as e:
            print(
                f"""
                -------ERRORS-------
                {error_lines}

                Run for more detailed output:
                    env PYTHONPATH=src:$PYTHONPATH python -m tests-manual.update_test_data -t {errors} --verbose --globus_token "" --manual_test --dry_run
                """
            )
            raise e

    def get_paths(self):
        self.dataset_paths = {}
        for test_dir in self.dataset_test_dirs:
            metadata_paths = [path for path in Path(f"{test_dir}/upload").glob("*metadata.tsv")]
            self.dataset_paths[test_dir] = metadata_paths

    def test_validate_dataset_examples(self, verbose: bool = False, full_diff: bool = False):
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
                        try:
                            dataset_test(
                                test_dir,
                                opts,
                                verbose=verbose,
                                offline=True,
                                use_online_check_fixtures=True,
                                full_diff=full_diff,
                            )
                        except MockException as e:
                            print(e)
                            continue
                        except AssertionError as e:
                            print(e)
                            self.errors.append(test_dir)
                            continue

    @staticmethod
    def prep_offline_upload(test_dir: str, opts: Dict) -> Upload:
        with patch(
            "ingest_validation_tools.validation_utils.get_assaytype_data",
            side_effect=lambda row, ingest_url, globus_token: assaytype_side_effect(
                test_dir, row, ingest_url, globus_token
            ),
        ):
            with patch("ingest_validation_tools.validation_utils.get_entity_api_data"):
                with patch("ingest_validation_tools.upload.Upload.online_checks"):
                    upload = Upload(Path(f"{test_dir}/upload"), **opts)
                    upload.get_errors()
                    upload = mutate_upload_errors_with_fixtures(upload, test_dir)
                    upload.get_info()
                    return upload

    def prep_dir_schema_upload(self, test_dir: str, opts: Dict, patch_data: Dict) -> Upload:
        with patch(
            "ingest_validation_tools.validation_utils.get_assaytype_data",
            side_effect=lambda row, ingest_url, globus_token: assaytype_side_effect(
                test_dir, row, ingest_url, globus_token
            ),
        ):
            with patch(
                "ingest_validation_tools.validation_utils.get_possible_directory_schemas",
            ) as dir_schemas_func_patch:
                with patch("ingest_validation_tools.upload.Upload.online_checks"):
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
            for path in upload.effective_tsv_paths.keys():
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
            for path in upload.effective_tsv_paths.keys():
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
            for path in upload.effective_tsv_paths.keys():
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
            for path in upload.effective_tsv_paths.keys():
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
            with patch("ingest_validation_tools.upload.Upload.online_checks"):
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
            "examples/dataset-examples/good-scatacseq-metadata-v0": {},
            "examples/dataset-examples/bad-mixed": {
                "Preflight Errors": "Found multiple dataset types in upload: CODEX, SNARE-seq2"
            },
        }
        for test_dir, expected_counts in test_dirs.items():
            upload = self.prep_offline_upload(test_dir, DATASET_EXAMPLES_OPTS)
            report = ErrorReport(upload)
            self.assertEqual(report.counts, expected_counts)


# if __name__ == "__main__":
#     suite = unittest.TestLoader().loadTestsFromTestCase(TestDatasetExamples)
#     suite.debug()
