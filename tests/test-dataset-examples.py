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
    if not response_dict:
        # TODO: add directions for creating mock response file
        raise MockException(
            f"""
                No mock response file exists for {path}. Run to generate:
                """
        )
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
        mock_response_file = open(Path(path) / "MOCK_RESPONSE.json")
        return json.load(mock_response_file)
    except Exception:
        return {}


# TODO: add this to online testing
# def compare_mock_with_response(row: Dict, response: Dict, path: Path):
#     mock_file = open_and_read_mock_file(path)
#     # Messy method of creating mock response file if missing or outdated;
#     # would be nicer for this to throw exception during testing and have
#     # user create manually
#     dataset_type = _get_dataset_type_from_row(row)
#     for dataset_type_key, mock in mock_file.items():
#         if dataset_type == dataset_type_key:
#             if row.values() == mock.get("args") and response == mock.get(response):
#                 return
#     update_mock_file(row, path, response)
#
#
# def update_mock_file(row: Dict, path: Path, response: Dict):
#     metadata_dir = path.parents[1]
#     try:
#         with open(metadata_dir / "MOCK_RESPONSE.json", "r") as mock_file:
#             existing = json.load(mock_file)
#     except Exception:
#         existing = {}
#     # TODO: this will break if Other types get added to soft assay endpoint
#     dataset_type = _get_dataset_type_from_row(row)
#     existing[dataset_type] = {"args": list(row.values()), "response": response}
#     with open(metadata_dir / "MOCK_RESPONSE.json", "w") as f:
#         json.dump(existing, f)
#
#
# def _get_dataset_type_from_row(row: Dict):
#     return row.get("dataset_type") if row.get("dataset_type") else row.get("assay_type")


class TestDatasetExamples(unittest.TestCase):
    multi = []
    test_dirs = [
        test_dir
        for test_dir in [
            *glob.glob("examples/dataset-examples/**"),
            *glob.glob("examples/dataset-iec-examples/**"),
            *glob.glob("examples/tsv-examples/**"),
        ]
        if Path(test_dir).is_dir()
    ]

    @patch("ingest_validation_tools.validation_utils.get_assaytype_data")
    def test_validate_single_assaytype_dataset_examples(self, mock_assaytype_data):
        opts = {
            "dataset_ignore_globs": ["ignore-*.tsv", ".*"],
            "upload_ignore_globs": ["drv_ignore_*", "README_ONLINE"],
            "run_plugins": True,
        }
        for test_dir in self.test_dirs:
            dir_path = Path(f"{test_dir}/upload")
            tsv_paths = [path for path in dir_path.glob("*metadata.tsv")]
            # TODO: write test for multi-assay
            if len(tsv_paths) > 1:
                self.multi.append(test_dir)
                continue
            mock_assaytype_data.return_value = mock_response(test_dir, multi=False)
            with open(tsv_paths[0], encoding="ascii") as f:
                rows = list(DictReader(f, dialect="excel-tab"))
            print(f"Testing {test_dir}...")
            readme = open(f"{test_dir}/README.md", "r")
            upload = Upload(dir_path, **opts)
            info = upload.get_info()
            mock_assaytype_data.assert_called_with(rows[0], upload.app_context["ingest_url"])
            errors = upload.get_errors()
            report = ErrorReport(info=info, errors=errors)
            d = difflib.Differ()
            diff = list(d.compare(readme.readlines(), report.as_md().splitlines(keepends=True)))
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
                  DIFF NEW LINES:
                  {new}
                  DIFF REMOVED LINES:
                  {removed}
                  """
