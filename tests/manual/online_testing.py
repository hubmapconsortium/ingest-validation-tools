from datetime import datetime
from pathlib import Path

from vcr import VCR
from vcr.request import Request

from tests.manual.updaters import (
    DATETIME_FORMAT,
    DryRunPersister,
    LiveRunPersister,
    raise_or_print_fatal_errors,
)
from tests.vcr_utils import vcr_create_upload_and_diff


class OnlineTesting:
    def __init__(
        self,
        paths: list[str | Path],
        globus_token: str,
        dry_run=True,
    ):
        """
        Arguments:
            paths: list of example dir paths to test
            globus_token: Globus API token
            dry_run:
                True: run online tests and print updates
                False: run online tests and update fixtures/readmes

        """
        self.paths = [Path(path) for path in paths]
        self.dry_run = dry_run
        self.globus_token = globus_token
        self.live_tests()

    def before_record_request(self, request: Request) -> Request:
        request.headers = None
        return request

    def before_record_response(self, response: dict) -> dict:
        response["headers"] = {}
        response["datetime"] = datetime.now().strftime(DATETIME_FORMAT)
        raise_or_print_fatal_errors(response["body"]["string"].decode("utf-8"))
        return response

    @property
    def my_vcr(self) -> VCR:
        my_vcr = VCR(
            record_on_exception=False,
            before_record_request=self.before_record_request,
            before_record_response=self.before_record_response,
            serializer="json",
        )
        if self.dry_run:
            my_vcr.register_persister(DryRunPersister)
        else:
            my_vcr.register_persister(LiveRunPersister)
        return my_vcr

    def live_test(self, path: Path):
        # TODO: make single dir live tests
        print(f"Testing {path}...")
        vcr_create_upload_and_diff(path, self.globus_token, record_mode="all", vcr=self.my_vcr)

    def live_tests(self):
        for path in self.paths:
            self.live_test(path)
