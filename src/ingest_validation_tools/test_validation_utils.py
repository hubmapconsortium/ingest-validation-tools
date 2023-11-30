import json
from pathlib import Path
from typing import Dict, List


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
    diff = set(row.values()).difference(response_dict.get("args", []))
    if not diff:
        return response_dict["response"]
    else:
        raise MockException(
            f"""
            Not all expected args were passed for path {path}.
            Diff: {diff}
            Args passed: {row}
            Expected args: {response_dict.get("args", [])}
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
    if not row.values() == mock_file.get("args") or not response == mock_file.get(
        "response"
    ):
        update_mock_file(list(row.values()), path, response)


def update_mock_file(row: List, path: Path, response: Dict, method: str = "w"):
    metadata_dir = path.parents[1]
    with open(metadata_dir / "MOCK_RESPONSE.json", method) as mock_file:
        json.dump({"args": row, "response": response}, mock_file)
