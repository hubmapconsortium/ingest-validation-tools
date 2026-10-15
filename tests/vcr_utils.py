import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from deepdiff import DeepDiff, Delta
from vcr import VCR
from vcr.persisters.filesystem import (
    FilesystemPersister,
)
from vcr.request import Request
from vcr.serialize import serialize

from ingest_validation_tools.upload import Upload

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

SHARED_OPTS: dict = {
    "encoding": "ascii",
}
DATASET_EXAMPLES_OPTS: dict = SHARED_OPTS | {
    "dataset_ignore_globs": ["ignore-*.tsv", ".*"],
    "upload_ignore_globs": ["drv_ignore_*"],
}
DATASET_IEC_EXAMPLES_OPTS: dict = SHARED_OPTS | {
    "dataset_ignore_globs": ["metadata.tsv"],
    "upload_ignore_globs": ["*"],
}
PLUGIN_EXAMPLES_OPTS: dict = DATASET_EXAMPLES_OPTS | {
    "plugin_directory": "../ingest-validation-tests/src/ingest_validation_tests/",
    "run_plugins": True,
    "offline_only": True,
}


def create_upload(dataset_path: Path, globus_token: str) -> Upload:
    if "dataset-examples" in dataset_path.parts:
        opts = DATASET_EXAMPLES_OPTS
    elif "dataset-iec-examples" in dataset_path.parts:
        opts = DATASET_IEC_EXAMPLES_OPTS
    elif "plugin-tests" in dataset_path.parts:
        opts = PLUGIN_EXAMPLES_OPTS
    else:
        opts = {}
    return Upload(Path(f"{dataset_path}/upload"), globus_token=globus_token, **opts)


class LiveTesting:
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
                False: run online tests and update fixtures

        """
        self.paths = [Path(path) for path in paths]
        self.dry_run = dry_run
        self.globus_token = globus_token
        self.responses = {}
        self.live_tests()
        self.current_cassette = None

    def before_record_request(self, request: Request):
        request.headers = None
        return request

    def before_record_response(self, response):
        response["headers"] = {}
        response["datetime"] = datetime.now().strftime(DATETIME_FORMAT)
        self.raise_or_print_fatal_errors(response["body"]["string"].decode("utf-8"))
        return response

    def raise_or_print_fatal_errors(self, response_str: str):
        """
        Force stop before writing any files if fatal errors found:
            "Too Many Requests": CEDAR API is overloaded
            "Unauthorized"/"No token": Globus token not provided to entity-api for URL checks
            "500": unknown error
        """
        for error in [
            "Too Many Requests",
            "Unauthorized",
            "No token",
            "500 Internal Server Error",
        ]:
            print(response_str)
            if error in response_str:
                # Necessary to avoid including 'Unauthorized' in output when no Globus token is provided,
                # but only relevant for entity-api links
                if error in ["Unauthorized for url: https://entity.api", "No token"]:
                    msg = f"URL checking returned 'Unauthorized' in response; did you forget a Globus token?"
                else:
                    msg = f"Something went wrong with a request: {error}"
                if not self.dry_run:
                    raise Exception(msg)
                print(f"Error: {msg}.")

    @property
    def my_vcr(self):
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
        # TODO: abstract so that live and offline testing
        # use the same method
        with self.my_vcr.use_cassette(
            path=path / "fixtures.json",
            record_mode="all",
            decode_compressed_response=True,
            match_on=["body"],
        ):
            print(f"Testing {path}...")
            upload = create_upload(path, self.globus_token)
            upload.get_errors()
            readme = open(Path(path) / "README.json")
            readme.close()
            # Diff report & readme
            # If diff and not dry_run:
            #   Write report to README
            # If not diff:
            #   Pass, log

    def live_tests(self):
        for path in self.paths:
            self.live_test(path)


class UpdateFixtures:
    """
    Handles finding newest responses, finding and printing diffs,
    and serializing/writing fixture data for LiveRunPersister and DryRunPersister.
    """

    def __init__(self, cassette_path: Path, cassette_dict: dict, serializer):
        self.cassette_path = cassette_path
        self.cassette_dict = cassette_dict
        self.serializer = serializer

    def get_diff(self, existing_data, new_data) -> bool:
        """
        Find diff between existing fixture data and new request/response data.
        Print readable diff.
        """
        diff = DeepDiff(
            existing_data,
            json.loads(serialize(new_data, self.serializer)),
            ignore_order=True,
            report_repetition=True,
            verbose_level=2,
            exclude_paths=["root[**]['datetime']"],
        )
        if diff:
            print(f"Diff found for {self.cassette_path}:")
            print(self.readable_diff(diff))
            return True
        else:
            print(f"No diff found for cassette {self.cassette_path}.")
            return False

    def readable_diff(self, diff: DeepDiff) -> list[str]:
        delta = Delta(diff, bidirectional=True)
        flat_rows = delta.to_flat_rows()
        simple_diff = []
        for change in flat_rows:
            entry = {}
            entry["key"] = change.path
            if "removed" in change.action:
                entry["old"] = change.value
                entry["new"] = "Removed"
            else:
                entry["old"] = change.old_value
                entry["new"] = change.value
            simple_diff.append(entry)
        return simple_diff

    def serialize_and_write(self, cassette_dict: dict | None = None):
        """
        Just rewrites starting data as a default;
        can overwrite if passed a cassette_dict.
        """
        if not cassette_dict:
            cassette_dict = self.cassette_dict
        data = serialize(cassette_dict, self.serializer)
        cassette_folder = self.cassette_path.parent
        if not cassette_folder.exists():
            cassette_folder.mkdir(parents=True)
        with self.cassette_path.open("w") as f:
            f.write(data)

    def get_new_data(self):
        """
        In order to send all requests to endpoints when running in dry_run=False,
        we need to set record_mode="all" on vcr.LiveTesting.my_vcr.
        However, this records *all* requests/responses, including duplicates.
        This custom persister class retains only the most recent request/response
        for a given request (matched on endpoint/method).
        """
        new_data = defaultdict(list)
        by_request = defaultdict(lambda: defaultdict(list))
        # Organize all responses by request to identify duplicates
        for request, response in zip(
            self.cassette_dict["requests"], self.cassette_dict["responses"]
        ):
            by_request[str(request)]["request"] = request
            by_request[str(request)]["responses"].append(response)
        # Add request and most recent/latest response to new_data
        new_data = {"requests": [], "responses": []}
        for request_details in by_request.values():
            responses = request_details["responses"]
            if len(responses) > 1:
                latest_response = None
                latest_response_datetime = datetime.min
                for resp in responses:
                    response_datetime = datetime.strptime(resp["datetime"], DATETIME_FORMAT)
                    if latest_response_datetime and (response_datetime > latest_response_datetime):
                        latest_response_datetime = response_datetime
                    latest_response = resp
                new_data["requests"].append(request)
                new_data["responses"].append(latest_response)
            else:
                new_data["requests"].append(request)
                new_data["responses"].append(responses[0])
        return dict(new_data)


class LiveRunPersister(FilesystemPersister):
    @staticmethod
    def save_cassette(cassette_path, cassette_dict, serializer):
        updater = UpdateFixtures(cassette_path, cassette_dict, serializer)
        if not cassette_path.exists():
            updater.serialize_and_write()
            return
        with cassette_path.open("r") as f:
            existing_data = json.load(f)
        new_data = updater.get_new_data()
        if updater.get_diff(existing_data, new_data):
            print(f"Writing new data to {cassette_path}...")
            updater.serialize_and_write(new_data)


class DryRunPersister(FilesystemPersister):
    @staticmethod
    def save_cassette(cassette_path, cassette_dict, serializer):
        if not cassette_path.exists():
            print("Would create new cassette with data:")
            data = serialize(cassette_dict, serializer)
            print(data)
            return
        updater = UpdateFixtures(cassette_path, cassette_dict, serializer)
        with cassette_path.open("r") as f:
            existing_data = json.load(f)
        new_data = updater.get_new_data()
        if updater.get_diff(existing_data, new_data):
            print(f"DRY RUN, fixture data not changed.")
