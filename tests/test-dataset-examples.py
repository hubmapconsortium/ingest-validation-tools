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


def mock_response(path: str, multi: bool = False) -> Dict:
    response_dict = open_and_read_mock_file(path)
    if len(response_dict.keys()) > 1 and not multi:
        raise MockException(
            f"Single assay upload {path} has multiple assay types in mock response JSON file."
        )
    # TODO: add multi
    elif multi:
        raise NotImplementedError("")
    # TODO: fix returns after implementing multi-assay
    for _, response in response_dict.items():
        return response
    return {}


def open_and_read_mock_file(path: str) -> Dict:
    try:
        with open(Path(path) / "MOCK_RESPONSE.json") as f:
            opened = json.load(f)
            f.close()
    except json.JSONDecodeError:
        return {}
    return opened


class TestDatasetExamples(unittest.TestCase):
    multi = []
    no_tsv = []
    test_dirs = [
        test_dir
        for test_dir in [
            *glob.glob("examples/dataset-examples/**"),
            *glob.glob("examples/dataset-iec-examples/**"),
        ]
        if Path(test_dir).is_dir()
    ]

    @property
    def dataset_opts(self):
        return {
            "dataset_ignore_globs": ["ignore-*.tsv", ".*"],
            "upload_ignore_globs": ["drv_ignore_*", "README_ONLINE"],
            "run_plugins": True,
        }

    def test_for_diff(self, test_dir, readme, report):
        d = difflib.Differ()
        diff = list(d.compare(readme.readlines(), report.as_md().splitlines(keepends=True)))
        readme.close()
        ignore_strings = ["Time:", "Git version:", "```"]
        cleaned_diff = [
            line
            for line in diff
            if not any(ignore_string in line for ignore_string in ignore_strings)
        ]
        removed = "".join(x for x in cleaned_diff if x.startswith("- "))
        new = "".join(x for x in cleaned_diff if x.startswith("+ "))
        assert not (
            new and removed
        ), f"""
                New version:
                {''.join([line for line in diff])}

                DIFF NEW LINES:
                {new}

                DIFF REMOVED LINES:
                {removed}

                If new version is correct, overwrite previous README.md and MOCK_RESPONSE.json files by running:
                    env PYTHONPATH=src:$PYTHONPATH python -m tests-manual.update_readme -t {test_dir} -g <globus_token>

                For help / other options:
                    env PYTHONPATH=src:$PYTHONPATH python -m tests-manual.update_readme --help
                """
        print(f"PASSED: {test_dir}")

    @patch("ingest_validation_tools.validation_utils.get_assaytype_data")
    @patch("ingest_validation_tools.upload.Upload._check_matching_urls")
    def test_validate_single_assaytype_dataset_examples(self, mock_urls, mock_assaytype_data):
        for test_dir in self.test_dirs:
            # TODO: write test for multi-assay
            tsv_paths = [path for path in Path(f"{test_dir}/upload").glob("*metadata.tsv")]
            if len(tsv_paths) > 1:
                self.multi.append(test_dir)
                continue
            elif not tsv_paths:
                self.no_tsv.append(test_dir)
                continue
            mock_assaytype_data.return_value = mock_response(test_dir, multi=False)
            with open(tsv_paths[0], encoding="ascii") as f:
                rows = list(DictReader(f, dialect="excel-tab"))
            print(f"Testing {test_dir}...")
            readme = open(f"{test_dir}/README.md", "r")
            upload = Upload(Path(f"{test_dir}/upload"), **self.dataset_opts)
            f.close()
            info = upload.get_info()
            errors = upload.get_errors()
            report = ErrorReport(info=info, errors=errors)
            self.test_for_diff(test_dir, readme, report)
            mock_assaytype_data.assert_called_with(rows[0], upload.app_context["ingest_url"])
