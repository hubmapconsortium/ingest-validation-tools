import json
from collections import defaultdict
from pathlib import Path

from vcr.persisters.filesystem import (
    FilesystemPersister,
)
from vcr.serialize import serialize


class LivePersister(FilesystemPersister):
    @staticmethod
    def no_new_data_msg(cassette_path):
        return f"No new data to write to cassette {cassette_path}."

    @staticmethod
    def save_cassette(cassette_path, cassette_dict, serializer):
        """
        In order to send all requests to endpoints when running in dry_run=False,
        need to set record_mode="all" on the cassette. However, this would then record
        all requests/responses, including duplicates. This custom persister class
        checks the new data (cassette_dict = existing fixtures + new request/response data)
        against existing data in order to deduplicate, keeping the fixtures.json files
        (hopefully) 1:1 with the requests made during validation.
        """
        cassette_path = Path(cassette_path)
        if cassette_path.exists():
            new_data = defaultdict(list)
            with cassette_path.open("r") as f:
                existing_data = json.load(f)
                for request, response in zip(
                    cassette_dict["requests"], cassette_dict["responses"]
                ):
                    response["body"]["string"] = response["body"]["string"]
                    new_data = LivePersister.get_new_data(
                        existing_data, request, response, new_data, cassette_path
                    )
            if not new_data:
                print(LivePersister.no_new_data_msg(cassette_path))
                return
            cassette_dict = dict(new_data)
        LivePersister.serialize_and_write(cassette_dict, cassette_path, serializer)

    @staticmethod
    def get_new_data(existing_data, request, response, new_data, cassette_path):
        match = False
        msg = None
        for pair in existing_data["interactions"]:
            # Attempt to find a match between request/response pair in cassette_dict
            # and existing fixture data
            if LivePersister.compare(pair, request, response):
                # Want to add the first match to new_data and move on after matching
                if response not in new_data["responses"]:
                    msg = "Existing match found, retaining in fixtures.json."
                    break
                # Duplicate, do not want to (re-)add to new_data
                msg = "Matching request/response found, not adding to cassette."
                match = True
                break
        # Either match not found or initial match not yet written to new_data
        if not match:
            print(
                msg if msg else f"New request/response found, adding to cassette {cassette_path}."
            )
            new_data["requests"].append(request)
            new_data["responses"].append(response)
        return new_data

    @staticmethod
    def compare(pair, request, response):
        if (
            (pair["request"]["method"] == request.method)
            and (pair["request"]["uri"] == request.uri)
            and (pair["request"]["body"] == request.body.decode("utf-8"))
            and pair["response"]["body"]["string"] == response["body"]["string"]
        ):
            return True

    @staticmethod
    def serialize_and_write(cassette_dict: dict, cassette_path: Path, serializer):
        data = serialize(cassette_dict, serializer)

        cassette_folder = cassette_path.parent
        if not cassette_folder.exists():
            cassette_folder.mkdir(parents=True)
        with cassette_path.open("w") as f:
            f.write(data)


class DryRunPersister(LivePersister):
    @staticmethod
    def save_cassette(cassette_path, cassette_dict, serializer):
        del serializer
        cassette_path = Path(cassette_path)
        if cassette_path.exists():
            new_data = None
            with cassette_path.open("r") as f:
                existing_data = json.load(f)
                for request, response in zip(
                    cassette_dict["requests"], cassette_dict["responses"]
                ):
                    response["body"]["string"] = response["body"]["string"]
                    LivePersister.get_new_data(
                        existing_data, request, response, new_data, cassette_path
                    )

    @staticmethod
    def no_new_data_msg(cassette_path):
        return f"New request/response found, would add to cassette {cassette_path} (running in dry_run mode)."

    @staticmethod
    def get_new_data(existing_data, request, response, new_data, cassette_path):
        new_data = defaultdict(list)
        match = False
        for pair in existing_data["interactions"]:
            if LivePersister.compare(pair, request, response):
                # We don't care what kind of match it is
                match = True
                break
        if not match:
            new_data["requests"].append(request)
            new_data["responses"].append(response)
            print(DryRunPersister.no_new_data_msg(cassette_path))
        if new_data:
            print(new_data)
        return {}
