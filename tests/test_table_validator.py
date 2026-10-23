from glob import glob
from pathlib import Path

from vcr.request import Request
from vcr.unittest import VCRTestCase
from yaml import safe_load

from ingest_validation_tools.local_validation.table_validator import get_table_errors
from tests.utils import get_paths


class TestTableValidator(VCRTestCase):

    def before_record_request(self, request: Request) -> Request:
        """
        Strip headers.
        """
        request.headers = None
        return request

    def before_record_response(self, response: dict) -> dict:
        """
        Strip headers, raise if Unauthorized, 500, No token errors.
        """
        response["headers"] = {}
        return response

    def _get_vcr(self, **kwargs):
        kwargs["before_record_request"] = self.before_record_request
        kwargs["before_record_response"] = self.before_record_response
        kwargs["cassette_library_dir"] = "tests/fixtures/cassettes"
        myvcr = super(TestTableValidator, self)._get_vcr(**kwargs)
        return myvcr

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
            "https://entity.api.hubmapconsortium.org/entities/f9ae931b8b49252f150d7f8bf1d2d13f": "200",
            "https://portal.hubmapconsortium.org/": "200",
            "https://entity.api.hubmapconsortium.org/entities/bad": "400",
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
