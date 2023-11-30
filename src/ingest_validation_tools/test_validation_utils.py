import json
from pathlib import Path
from typing import Dict


class MockException(Exception):
    def __init__(self, error):
        super().__init__(error)


def mock_response(path: Path, row: Dict) -> Dict:
    response_dict = open_and_read_mock_file(path)
    if not response_dict:
        raise MockException(
            f"""
                No mock response file exists for {path}. Run to generate:
                ./tests-manual/test-dataset-examples-cedar.sh <globus_token>
                """
        )
    dataset_type = _get_dataset_type_from_row(row)
    response_args = response_dict.get(dataset_type, {}).get("args", [])
    diff = set(row.values()).difference(response_args)
    if not diff:
        return response_dict[dataset_type]["response"]
    else:
        raise MockException(
            f"""
            Not all expected args were passed for path {path}.
            Diff: {diff}
            Args passed: {row}
            Expected args: {response_args}
            """
        )


def open_and_read_mock_file(path: Path) -> Dict:
    metadata_dir = path.parents[1]
    try:
        mock_response_file = open(metadata_dir / "MOCK_RESPONSE.json")
        return json.load(mock_response_file)
    except Exception:
        return {}


def compare_mock_with_response(row: Dict, response: Dict, path: Path):
    mock_file = open_and_read_mock_file(path)
    # Messy method of creating mock response file if missing or outdated;
    # would be nicer for this to throw exception during testing and have
    # user create manually
    dataset_type = _get_dataset_type_from_row(row)
    for dataset_type_key, mock in mock_file.items():
        if dataset_type == dataset_type_key:
            if row.values() == mock.get("args") and response == mock.get(response):
                return
    update_mock_file(row, path, response)


def update_mock_file(row: Dict, path: Path, response: Dict):
    metadata_dir = path.parents[1]
    try:
        with open(metadata_dir / "MOCK_RESPONSE.json", "r") as mock_file:
            existing = json.load(mock_file)
    except Exception:
        existing = {}
    # TODO: this will break if Other types get added to soft assay endpoint
    dataset_type = _get_dataset_type_from_row(row)
    existing[dataset_type] = {"args": list(row.values()), "response": response}
    with open(metadata_dir / "MOCK_RESPONSE.json", "w") as f:
        json.dump(existing, f)


def _get_dataset_type_from_row(row: Dict):
    return row.get("dataset_type") if row.get("dataset_type") else row.get("assay_type")
