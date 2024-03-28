import difflib
import glob
import json
import re
import unittest
from csv import DictReader
from io import TextIOWrapper
from pathlib import Path
from typing import Dict, List
from unittest.mock import Mock, call, patch

from ingest_validation_tools.error_report import ErrorReport
from ingest_validation_tools.upload import Upload

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


def dataset_test(test_dir: str, dataset_opts: Dict, verbose: bool = False):
    dataset_opts = dataset_opts | {"verbose": verbose}
    print(f"Testing {test_dir}...")
    readme = open(f"{test_dir}/README.md", "r")
    upload = Upload(Path(f"{test_dir}/upload"), **dataset_opts)
    info = upload.get_info()
    errors = upload.get_errors()
    report = ErrorReport(errors=errors, info=info)
    diff_test(test_dir, readme, clean_report(report), verbose=verbose)
    if "PreflightError" in report.as_md():
        raise MockException(
            f"Error report for {test_dir} contains PreflightError, do not make assertions about calls."
        )


def clean_report(report: ErrorReport):
    clean_report = []
    regex = re.compile(r"((Time|Git version): )(.*)")
    for line in report.as_md():
        match = regex.search(line)
        if match:
            new_line = line.replace(match.group(3), "WILL_CHANGE")
            clean_report.append(new_line)
        else:
            clean_report.append(line)
    return "".join(clean_report)


def diff_test(
    test_dir: str,
    readme: TextIOWrapper,
    report: str,
    verbose: bool = True,
):
    d = difflib.Differ()
    diff = list(d.compare(readme.readlines(), report.splitlines(keepends=True)))
    readme.close()
    ignore_strings = ["Time:", "Git version:", "```"]
    cleaned_diff = [
        line for line in diff if not any(ignore_string in line for ignore_string in ignore_strings)
    ]
    new = "".join([line.strip() for line in cleaned_diff if line.startswith("+ ")])
    removed = "".join([line.strip() for line in cleaned_diff if line.startswith("- ")])
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


def _online_side_effect(schema_name: str, dir_path: str, *args):
    del args
    fixture = _open_and_read_fixtures_file(dir_path)
    return fixture.get("validation", {}).get(schema_name, {})


def _assaytype_side_effect(path: str, row: Dict, *args, **kwargs):
    del args, kwargs
    response_dict = _open_and_read_fixtures_file(path)
    dataset_type = row.get("assay_type") if row.get("assay_type") else row.get("dataset_type")
    return response_dict.get("assaytype", {}).get(dataset_type)


class TestDatasetExamples(unittest.TestCase):
    dataset_paths = {}
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
        errors = "\n".join([str(error) for error in self.errors])
        try:
            self.assertEqual([], self.errors)
        except AssertionError:
            print(
                f"""-------ERRORS-------
                    {errors}
                """
            )

    def get_paths(self):
        for test_dir in self.dataset_test_dirs:
            metadata_paths = [path for path in Path(f"{test_dir}/upload").glob("*metadata.tsv")]
            self.dataset_paths[test_dir] = metadata_paths

    def test_validate_dataset_examples(self, verbose: bool = False):
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
                    with patch(
                        "ingest_validation_tools.upload.Upload.online_checks",
                        side_effect=lambda tsv_path, schema_name, report_type: _online_side_effect(
                            schema_name, test_dir, tsv_path, report_type
                        ),
                    ):
                        try:
                            dataset_test(test_dir, opts, verbose=verbose)
                        except MockException as e:
                            print(e)
                            continue
                        except AssertionError as e:
                            print(e)
                            self.errors.append(e)
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
