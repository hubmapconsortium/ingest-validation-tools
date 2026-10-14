import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from deepdiff import DeepDiff, Delta
from vcr.persisters.filesystem import (
    FilesystemPersister,
)
from vcr.serialize import serialize

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


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
