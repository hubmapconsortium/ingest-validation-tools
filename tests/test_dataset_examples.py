import difflib
import glob
import json
import re
import unittest
from csv import DictReader
from io import TextIOWrapper
from pathlib import Path
from typing import Dict
from unittest.mock import patch

from ingest_validation_tools.error_report import ErrorReport
from ingest_validation_tools.upload import Upload

# TODO: write tests for multi-assay, TSV
SINGLE_DATASET_OPTS = {
    "dataset_ignore_globs": ["ignore-*.tsv", ".*"],
    "upload_ignore_globs": ["drv_ignore_*"],
    "encoding": "ascii",
    "run_plugins": True,
}


class MockException(Exception):
    def __init__(self, error):
        super().__init__(error)


def mock_assaytype_response(path: str, multi: bool = False) -> Dict:
    response_dict = open_and_read_fixtures_file(path)
    section = response_dict.get("assaytype", {})
    if len(section.keys()) > 1 and not multi:
        raise MockException(
            f"Single assay upload {path} has multiple assay types in fixtures.json > 'assaytype'."
        )
    # TODO: add multi
    elif multi:
        raise NotImplementedError("")
    # TODO: fix returns after implementing multi-assay
    for _, response in section.items():
        return response
    return {}


def mock_spreadsheet_validator_response_data(path: str, multi: bool = False) -> Dict:
    response_dict = open_and_read_fixtures_file(path)
    section = response_dict.get("validation", {})
    if len(section.keys()) > 1 and not multi:
        raise MockException(
            f"Single assay upload {path} has multiple assay types in fixtures.json file."
        )
    # TODO: add multi
    elif multi:
        raise NotImplementedError("")
    return section


def open_and_read_fixtures_file(path: str) -> Dict:
    try:
        with open(Path(path) / "fixtures.json") as f:
            opened = json.load(f)
            f.close()
    except json.JSONDecodeError:
        return {}
    return opened


def single_dataset_test(test_dir: str, dataset_opts: Dict):
    print(f"Testing {test_dir}...")
    readme = open(f"{test_dir}/README.md", "r")
    upload = Upload(Path(f"{test_dir}/upload"), **dataset_opts)
    info = upload.get_info()
    with patch(
        "ingest_validation_tools.upload.Upload.online_checks",
        side_effect=lambda _tsv_path, schema_name, _report_type: online_side_effect(
            schema_name, test_dir
        ),
    ):
        errors = upload.get_errors()
    report = ErrorReport(info=info, errors=errors)
    test_for_diff(test_dir, readme, clean_report(report))


def clean_report(report):
    clean_report = []
    regex = re.compile(r"((Time|Git version): )(.*)")
    for line in report.as_md().splitlines(keepends=True):
        match = regex.search(line)
        if match:
            new_line = line.replace(match.group(3), "WILL_CHANGE")
            clean_report.append(new_line)
        else:
            clean_report.append(line)
    return "".join(clean_report)


def online_side_effect(schema_name: str, dir_path: str):
    fixture = open_and_read_fixtures_file(dir_path)
    return fixture.get("validation", {}).get(schema_name)


def test_for_diff(test_dir: str, readme: TextIOWrapper, report: str, verbose: bool = True):
    d = difflib.Differ()
    diff = list(d.compare(readme.readlines(), report.splitlines(keepends=True)))
    readme.close()
    ignore_strings = ["Time:", "Git version:", "```"]
    cleaned_diff = [
        line for line in diff if not any(ignore_string in line for ignore_string in ignore_strings)
    ]
    msg = f"DIFF FOUND: {test_dir}"
    new = "".join([line.strip() for line in cleaned_diff if line.startswith("+ ")])
    removed = "".join([line.strip() for line in cleaned_diff if line.startswith("- ")])
    if verbose:
        msg = f"""
                NEW VERSION:
                {new}

                DIFF REMOVED LINES:
                {removed}

                If new version is correct, overwrite previous README.md and fixtures.json files by running:
                    env PYTHONPATH=src:$PYTHONPATH python -m tests-manual.update_test_data -t {test_dir} -g <globus_token>

                For help / other options:
                    env PYTHONPATH=src:$PYTHONPATH python -m tests-manual.update_test_data --help
                """
    assert not new and not removed, msg
    print(f"PASSED: {test_dir}")


class TestDatasetExamples(unittest.TestCase):
    single = {}
    multi = {}
    no_tsv = {}
    test_dirs = [
        test_dir
        for test_dir in [
            *glob.glob("examples/dataset-examples/**"),
            *glob.glob("examples/dataset-iec-examples/**"),
        ]
        if Path(test_dir).is_dir()
    ]

    def setUp(self) -> None:
        super().setUp()
        self.classify_dirs()

    def classify_dirs(self):
        for test_dir in self.test_dirs:
            # TODO: write test for multi-assay
            tsv_paths = [path for path in Path(f"{test_dir}/upload").glob("*metadata.tsv")]
            if len(tsv_paths) == 1:
                self.single[test_dir] = tsv_paths
            elif len(tsv_paths) > 1:
                self.multi[test_dir] = tsv_paths
                continue
            elif not tsv_paths:
                self.no_tsv[test_dir] = tsv_paths
                continue

    def test_validate_single_assaytype_dataset_examples(self):
        for test_dir, tsv_paths in self.single.items():
            with patch(
                "ingest_validation_tools.validation_utils.get_assaytype_data",
                return_value=mock_assaytype_response(test_dir, multi=False),
            ) as mock_assaytype_data:
                single_dataset_test(test_dir, SINGLE_DATASET_OPTS)
            with open(tsv_paths[0], encoding="ascii") as f:
                rows = list(DictReader(f, dialect="excel-tab"))
            f.close()
            mock_assaytype_data.assert_called_with(
                rows[0],
                "https://ingest.api.hubmapconsortium.org/",
                Path(tsv_paths[0]),
                offline=False,
            )
