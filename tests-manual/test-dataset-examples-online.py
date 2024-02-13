import difflib
import glob
import json
import unittest
from pathlib import Path
from typing import Dict

from ingest_validation_tools.error_report import ErrorReport
from ingest_validation_tools.upload import Upload

# TODO: write tests for multi-assay, TSV


class MockException(Exception):
    def __init__(self, error):
        super().__init__(error)


def mock_response(path: str) -> Dict:
    response_dict = open_and_read_mock_file(path)
    if not response_dict:
        # TODO: add directions for creating mock response file
        raise MockException(
            f"""
                No mock response file exists for {path}. Run to generate:
                """
        )
    return response_dict


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

    def test_validate_single_assaytype_dataset_examples(self):
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
            print(f"Testing {test_dir}...")
            readme = open(f"{test_dir}/README.md", "r")
            upload = Upload(dir_path, **opts)
            info = upload.get_info()
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
                  New version:
                  {''.join([line for line in diff])}

                  DIFF NEW LINES:
                  {new}

                  DIFF REMOVED LINES:
                  {removed}

                  If new version is correct, overwrite previous README.md and mock response with:
                    tests-manual/update_readme.py {test_dir} <globus_token>
                  """
