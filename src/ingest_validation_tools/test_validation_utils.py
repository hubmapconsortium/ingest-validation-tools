import json
from pathlib import Path
from typing import Dict, Optional


class MockException(Exception):
    def __init__(self, error):
        super().__init__(error)


def mock_response(
    path: Path, dataset_type: str, metadata_schema_id: Optional[str], is_cedar: bool
) -> Dict:
    response_dict = open_and_read_mock_file(path)
    if not response_dict:
        raise MockException(
            f"""
                No mock response file exists for {path}. Run to generate:
                ./tests-manual/test-dataset-examples-cedar.sh <globus_token>
                """
        )
    request_args = [dataset_type, metadata_schema_id, is_cedar]
    if not set(request_args).difference(response_dict.get("args", {}).values()):
        return response_dict["response"]
    else:
        raise MockException(
            f"""
            Not all expected args were passed for path {path}.
            Args passed: {request_args}
            Expected args: {list(response_dict.get("args", {}).values())}
            """
        )


def open_and_read_mock_file(path: Path) -> Dict:
    metadata_dir = path.parents[1]
    try:
        mock_response_file = open(metadata_dir / "MOCK_RESPONSE.json")
        return json.load(mock_response_file)
    except Exception:
        return {}


def compare_mock_with_response(request_args: Dict, response: Dict, path: Path):
    mock_file = open_and_read_mock_file(path)
    # Messy method of creating mock response file if missing or outdated;
    # would be nicer for this to throw exception during testing and have
    # user create manually
    if not request_args == mock_file.get("args") or not response == mock_file.get(
        "response"
    ):
        update_mock_file(request_args, path, response)


def update_mock_file(request_args: Dict, path: Path, response: Dict, method: str = "w"):
    metadata_dir = path.parents[1]
    with open(metadata_dir / "MOCK_RESPONSE.json", method) as mock_file:
        json.dump({"args": request_args, "response": response}, mock_file)
