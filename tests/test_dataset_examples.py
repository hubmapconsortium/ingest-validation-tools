import difflib
import glob
import json
import unittest
from csv import DictReader
from pathlib import Path
from typing import Dict
from unittest.mock import patch

from ingest_validation_tools.error_report import ErrorReport
from ingest_validation_tools.upload import Upload

# TODO: write tests for multi-assay, TSV


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
    test_for_diff(test_dir, readme, report)


def online_side_effect(schema_name: str, dir_path: str):
    fixture = open_and_read_fixtures_file(dir_path)
    return fixture.get("validation", {}).get(schema_name)


def test_for_diff(test_dir, readme, report):
    d = difflib.Differ()
    diff = list(d.compare(readme.readlines(), report.as_md().splitlines(keepends=True)))
    readme.close()
    ignore_strings = ["Time:", "Git version:", "```"]
    cleaned_diff = [
        line for line in diff if not any(ignore_string in line for ignore_string in ignore_strings)
    ]
    removed = "".join(x for x in cleaned_diff if x.startswith("- "))
    new = "".join(x for x in cleaned_diff if x.startswith("+ "))
    assert not (
        new and removed
    ), f"""
            New version:
            {''.join([line for line in diff])}

            DIFF REMOVED LINES:
            {removed}

            If new version is correct, overwrite previous README.md and fixtures.json files by running:
                env PYTHONPATH=src:$PYTHONPATH python -m tests-manual.update_test_data -t {test_dir} -g <globus_token>

            For help / other options:
                env PYTHONPATH=src:$PYTHONPATH python -m tests-manual.update_readme --help
            """
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

    @property
    def dataset_opts(self):
        return {
            "dataset_ignore_globs": ["ignore-*.tsv", ".*"],
            "upload_ignore_globs": ["drv_ignore_*", "README_ONLINE"],
            "encoding": "ascii",
            "run_plugins": True,
        }

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
                single_dataset_test(test_dir, self.dataset_opts)
            with open(tsv_paths[0], encoding="ascii") as f:
                rows = list(DictReader(f, dialect="excel-tab"))
            f.close()
            mock_assaytype_data.assert_called_with(
                rows[0],
                "https://ingest.api.hubmapconsortium.org/",
                Path(tsv_paths[0]),
                offline=False,
            )
