import unittest
from glob import glob
from pathlib import Path

from yaml import safe_load

from ingest_validation_tools.local_validation.table_validator import get_table_errors
from tests.utils import get_paths


class TestTableValidator(unittest.TestCase):

    @property
    def example_dirs(self) -> list[Path]:
        return [
            Path(test_dir)
            for test_dir in [
                *glob("examples/custom-constraint-examples/**"),
            ]
            if Path(test_dir).is_dir()
        ]

    def test_custom_constraint_examples(self):
        status_cache = {
            "https://entity.api.hubmapconsortium.org/entities/f9ae931b8b49252f150d7f8bf1d2d13f": 200,
            "https://portal.hubmapconsortium.org/": 200,
            "https://entity.api.hubmapconsortium.org/entities/bad": 400,
            "bad://url": "No connection adapters were found for 'bad://url'",
        }
        for test_dir in get_paths(self.example_dirs):
            print(f"Testing {test_dir}...")
            tsv_path = test_dir / "input.tsv"
            schema_path = test_dir / "schema.yaml"
            with open(test_dir / "output.txt") as f:
                expected_errors = f.read().splitlines()
            errors, _ = get_table_errors(
                tsv_path, safe_load(schema_path.read_text()), status_cache
            )
            assert errors == [error for error in expected_errors if error != ""]
