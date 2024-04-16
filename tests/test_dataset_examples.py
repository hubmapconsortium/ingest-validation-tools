import difflib
import glob
import json
import re
import unittest
from collections import defaultdict
from csv import DictReader
from io import TextIOWrapper
from pathlib import Path
from typing import Dict, List, Union
from unittest.mock import Mock, call, patch

from ingest_validation_tools.error_report import ErrorDict, ErrorReport
from ingest_validation_tools.upload import Upload

from .fixtures import (
    SCATACSEQ_BOTH_VERSIONS_VALID,
    SCATACSEQ_HIGHER_VERSION_VALID,
    SCATACSEQ_LOWER_VERSION_VALID,
    SCATACSEQ_NEITHER_VERSION_VALID,
)

SHARED_OPTS = {
    "encoding": "ascii",
    "run_plugins": True,
}
DATASET_EXAMPLES_OPTS = SHARED_OPTS | {
    "dataset_ignore_globs": ["ignore-*.tsv", ".*"],
    "upload_ignore_globs": ["drv_ignore_*"],
}
DATASET_IEC_EXAMPLES_OPTS = SHARED_OPTS | {
    "dataset_ignore_globs": ["metadata.tsv"],
    "upload_ignore_globs": ["*"],
}
PLUGIN_EXAMPLES_OPTS = DATASET_EXAMPLES_OPTS | {
    "plugin_directory": "../ingest-validation-tests/src/ingest_validation_tests/"
}


class MockException(Exception):
    def __init__(self, error):
        super().__init__(error)


class TokenException(Exception):
    def __init__(self, error: str, clean_report: Union[str, Dict]):
        super().__init__(error)
        self.clean_report = clean_report


def mutate_upload_errors_with_fixtures(upload: Upload, test_dir: str) -> Upload:
    for tsv_path, schema in upload.effective_tsv_paths.items():
        fixtures = get_online_check_fixtures(schema.schema_name, test_dir)
        url_errors = fixtures.get("URL Check Errors", {})
        if url_errors:
            upload.errors.metadata_url_errors[tsv_path] = url_errors
        api_errors = fixtures.get("Spreadsheet Validator Errors", {})
        if api_errors:
            upload.errors.metadata_validation_api[tsv_path] = api_errors
        for other_type, paths in {
            "antibodies": schema.antibodies_paths,
            "contributors": schema.contributors_paths,
        }.items():
            for path in paths:
                other_fixtures = get_online_check_fixtures(other_type, test_dir)
                other_url_errors = other_fixtures.get("URL Errors", {})
                if other_url_errors:
                    upload.errors.metadata_url_errors[path] = other_url_errors
                other_api_errors = other_fixtures.get("Spreadsheet Validator Errors", {})
                if other_api_errors:
                    upload.errors.metadata_validation_api[path] = other_api_errors
    return upload


def dataset_test(
    test_dir: str,
    dataset_opts: Dict,
    verbose: bool = False,
    globus_token: str = "",
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
        upload = Upload(Path(f"{test_dir}/upload"), **dataset_opts, globus_token=globus_token)
    errors = upload.get_errors()
    info = upload.get_info()
    if use_online_check_fixtures:
        upload = mutate_upload_errors_with_fixtures(upload, test_dir)
    report = ErrorReport(errors=errors, info=info)
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
            f"WARNING: API token required to complete update, not writing, skipping URL Check Errors.",
            "".join(cleaned_report),
        )
    return "".join(cleaned_report)


def get_non_token_errors(errors: ErrorDict) -> ErrorDict:
    new_url_error_val = defaultdict(list)
    for path, error_list in errors.metadata_url_errors.items():
        non_token_url_errors = [error for error in error_list if not "No token" in error]
        if non_token_url_errors:
            new_url_error_val[path] = non_token_url_errors
        if set(error_list) - set(non_token_url_errors):
            print(
                f"WARNING: output about URL errors for {path} is incorrect. Use for testing purposes only."
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


def _assaytype_side_effect(path: str, row: Dict, *args, **kwargs):
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
        except AssertionError:
            print(
                f"""
                -------ERRORS-------
                {error_lines}

                Run for more detailed output:
                    env PYTHONPATH=src:$PYTHONPATH python -m tests-manual.update_test_data -t {errors} --verbose --globus_token "" --manual_test --dry_run
                """
            )

    def get_paths(self):
        self.dataset_paths = {}
        for test_dir in self.dataset_test_dirs:
            metadata_paths = [path for path in Path(f"{test_dir}/upload").glob("*metadata.tsv")]
            self.dataset_paths[test_dir] = metadata_paths

    def test_validate_dataset_examples(self, verbose: bool = False, full_diff: bool = False):
        for test_dir, tsv_paths in self.dataset_paths.items():
            with self.subTest(test_dir=test_dir):
                if "dataset-examples" in test_dir:
                    opts = DATASET_EXAMPLES_OPTS
                elif "dataset-iec-examples" in test_dir:
                    opts = DATASET_IEC_EXAMPLES_OPTS
                elif "plugin-tests" in test_dir:
                    opts = PLUGIN_EXAMPLES_OPTS
                else:
                    opts = {}
                with patch(
                    "ingest_validation_tools.validation_utils.get_assaytype_data",
                    side_effect=lambda row, ingest_url: _assaytype_side_effect(
                        test_dir, row, ingest_url
                    ),
                ) as mock_assaytype_data:
                    with patch("ingest_validation_tools.upload.Upload.online_checks"):
                        try:
                            dataset_test(
                                test_dir,
                                opts,
                                verbose=verbose,
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
                if len(tsv_paths) == 1:
                    self.single_dataset_assert(tsv_paths[0], mock_assaytype_data)
                elif len(tsv_paths) > 1:
                    self.multi_dataset_assert(tsv_paths, mock_assaytype_data)
                elif len(tsv_paths) == 0:
                    print(f"No TSVs found for {test_dir}, skipping further assertions.")

    def single_dataset_assert(self, tsv_path: str, mock_assaytype_data: Mock):
        with open(tsv_path, encoding="ascii") as f:
            try:
                rows = list(DictReader(f, dialect="excel-tab"))
            except UnicodeDecodeError:
                return
        f.close()
        if not rows:
            return
        if "assay_type" not in rows[0] or "dataset_type" not in rows[0]:
            return
        try:
            mock_assaytype_data.assert_called_with(
                rows[0],
                "https://ingest.api.hubmapconsortium.org/",
            )
        except AssertionError as e:
            print(e)
            self.errors.append(e)

    def multi_dataset_assert(self, tsv_paths: List[str], mock_assaytype_data: Mock):
        calls = []
        for tsv_path in tsv_paths:
            with open(tsv_path, encoding="ascii") as f:
                rows = list(DictReader(f, dialect="excel-tab"))
            f.close()
            calls.append(call(rows[0], "https://ingest.api.hubmapconsortium.org/"))
        try:
            mock_assaytype_data.assert_has_calls(calls, any_order=True)
        except AssertionError as e:
            print(e)
            self.errors.append(e)

    @staticmethod
    def prep_offline_upload(test_dir: str, opts: Dict) -> Upload:
        with patch(
            "ingest_validation_tools.validation_utils.get_assaytype_data",
            side_effect=lambda row, ingest_url: _assaytype_side_effect(test_dir, row, ingest_url),
        ):
            with patch("ingest_validation_tools.upload.Upload.online_checks"):
                upload = Upload(Path(f"{test_dir}/upload"), **opts)
                upload.get_errors()
                upload = mutate_upload_errors_with_fixtures(upload, test_dir)
                return upload

    def prep_upload(self, test_dir: str, opts: Dict, patch_data: Dict) -> Upload:
        with patch(
            "ingest_validation_tools.validation_utils.get_assaytype_data",
            side_effect=lambda row, ingest_url: _assaytype_side_effect(test_dir, row, ingest_url),
        ):
            with patch(
                "ingest_validation_tools.validation_utils.get_possible_directory_schemas",
                return_value=patch_data,
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
            upload = self.prep_upload(
                test_dir, DATASET_EXAMPLES_OPTS, SCATACSEQ_HIGHER_VERSION_VALID
            )
            info = upload.get_info()
            if info is None:
                raise Exception(f"Info should not be none")
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
            upload = self.prep_upload(
                test_dir, DATASET_EXAMPLES_OPTS, SCATACSEQ_LOWER_VERSION_VALID
            )
            info = upload.get_info()
            if info is None:
                raise Exception(f"Info should not be none")
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
            upload = self.prep_upload(
                test_dir, DATASET_EXAMPLES_OPTS, SCATACSEQ_BOTH_VERSIONS_VALID
            )
            info = upload.get_info()
            if info is None:
                raise Exception(f"Info should not be none")
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
            upload = self.prep_upload(
                test_dir, DATASET_EXAMPLES_OPTS, SCATACSEQ_NEITHER_VERSION_VALID
            )
            info = upload.get_info()
            if info is None:
                raise Exception(f"Info should not be none")
            for path in upload.effective_tsv_paths.keys():
                dir_schema_version = (
                    info.as_dict()
                    .get("TSVs", {})
                    .get(Path(path).name, {})
                    .get("Directory schema version")
                )
                self.assertEqual(dir_schema_version, None)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDatasetExamples)
    suite.debug()
