import json
import re
from collections import defaultdict
from datetime import datetime
from json.decoder import JSONDecodeError
from pathlib import Path
from pprint import pformat

from deepdiff import DeepDiff, Delta, operator
from vcr.persisters.filesystem import FilesystemPersister
from vcr.serialize import serialize

from ingest_validation_tools.error_report import ErrorReport

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


class MockException(Exception):
    def __init__(self, error):
        super().__init__(error)


def open_or_create_readme(dir: Path) -> dict:
    path = Path(dir / "README.json")
    if not path.exists():
        with open(path, "w") as f:
            json.dump({}, f)
    with open(path, "r") as f:
        try:
            readme = json.load(f)
        except JSONDecodeError:
            readme = {}
    return readme


def readable_diff(diff: DeepDiff) -> list[str]:
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


def raise_or_print_fatal_errors(response_str: str, dry_run: bool = True):
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
        if error in response_str:
            # Necessary to avoid including 'Unauthorized' in output when no Globus token is provided,
            # but only relevant for entity-api links
            if error in ["Unauthorized for url: https://entity.api", "No token"]:
                msg = f"URL checking returned 'Unauthorized' in response; did you forget a Globus token?"
            else:
                msg = f"Something went wrong with a request: {error}"
            if not dry_run:
                raise Exception(msg)
            print(f"Error: {msg}.")


class UpdateReadme:
    """
    Diff README.json error data and ErrorReport from testing.
    Either log changes or make changes to files directly.
    Create README.json if it does not exist (dry_run=False only).
    Agnostic regarding online vs. offline testing.
    """

    def __init__(self, test_dir: Path, dry_run: bool, verbose: bool, error_report: ErrorReport):
        """
        Arguments:
            test_dir: example dir to evaluate
            dry_run:
                True: print readme updates
                False: update readmes
            verbose: error message verbosity
            error_report: ErrorReport object for upload created from test_dir
        """
        self.test_dir = test_dir
        self.dry_run = dry_run
        self.verbose = verbose
        self.orig_report = error_report.as_text()
        self.error_report = self.check_report(error_report)

    @staticmethod
    def remove_minor_version(version_str: str) -> str:
        return re.sub(r"\.\d", ".*", version_str)

    def check_report(self, error_report: ErrorReport):
        """
        Ensure no token errors in output.
        Manipulate raw_errors/raw_info data to remove any
        directory minor versions in specified areas.
        """
        raise_or_print_fatal_errors(error_report.as_text())
        if error_report.errors:
            new_dir_errors = defaultdict()
            if dir_errors := error_report.raw_errors.directory:
                for key, value in dir_errors.items():
                    new_dir_errors[self.remove_minor_version(key)] = value
            new_local_errors = defaultdict()
            if local_validation_errors := error_report.raw_errors.metadata_validation_local:
                for key, value in local_validation_errors.items():
                    new_local_errors[self.remove_minor_version(key)] = value
            if new_dir_errors:
                error_report.raw_errors.directory.value = new_dir_errors
            if new_local_errors:
                error_report.raw_errors.metadata_validation_local.value = new_local_errors
            error_report.errors = error_report.raw_errors.as_dict()
        else:
            dir_schema_key = "Directory schema version"
            for key, value in error_report.raw_info.tsvs.items():
                dir_schema_version = value.get(dir_schema_key)
                if type(dir_schema_version) is str:
                    error_report.raw_info.tsvs[key][dir_schema_key] = self.remove_minor_version(
                        dir_schema_version
                    )
            error_report.info = error_report.raw_info.as_dict()
        return error_report

    def check_maybe_write_readme(self) -> str | None:
        """
        Check existing readme against new ErrorReport.
        If there is a difference, write new readme.
        May return a str summary of changes.
        """
        readme = open_or_create_readme(self.test_dir)
        if self.readme_diff(readme):
            return self.write_readme()

    def write_readme(self) -> str | None:
        if self.error_report.errors:
            report = self.error_report.errors
        else:
            self.error_report.raw_info.time = "WILL_CHANGE"
            self.error_report.raw_info.git = "WILL_CHANGE"
            report = self.error_report.raw_info.as_dict()
        if self.dry_run:
            print(
                f"""
                    Would have written the following report to {self.test_dir}/README.json:
                    {report}
                    """
            )
            return "README diff found"
        else:
            print(
                f"""
                    Writing the following report to {self.test_dir}/README.json:
                    {report}
                    """
            )
            with open(Path(self.test_dir / "README.json"), "w") as f:
                json.dump(report, f, indent=2)

    def readme_diff(self, readme: dict) -> bool:
        try:
            self.readme_diff_test(readme, self.error_report)
            print(f"No diff found, no update to {self.test_dir}/README.json")
        except MockException:
            print("Expected exception found for test, continuing.")
        except AssertionError as e:
            print(f"FAILED diff_test: {self.test_dir}/README.json")
            if str(e):
                print(str(e))
            return True
        return False

    def readme_diff_test(
        self,
        readme: dict,
        report: ErrorReport,
    ) -> dict:
        if report.errors:
            testing_readme = report.errors
        else:
            testing_readme = report.info
        diff = DeepDiff(
            readme,
            testing_readme,
            ignore_order=True,
            report_repetition=True,
            verbose_level=2,
            custom_operators=[IgnoreVersions()],
            exclude_paths=["root['Time']", "root['Git version']"],
        )
        simple_diff = readable_diff(diff)
        msg = ""
        if self.verbose:
            msg = f"""
                    DIFF FOUND:
                    {pformat(simple_diff, indent=2)}
                    """
            if self.dry_run:
                msg = f"""
                    {msg}

                    If new version is correct, overwrite previous README.json and fixtures.json files by running:
                        env PYTHONPATH=src:$PYTHONPATH python -m tests.manual.update_test_data -t {self.test_dir} -g <globus_token>

                    For help / other options:
                        env PYTHONPATH=src:$PYTHONPATH python -m tests.manual.update_test_data --help
                    """
        elif self.dry_run:
            msg = f"""
                    FAILED diff_test: {self.test_dir}. Run for more detailed output:
                        env PYTHONPATH=src:$PYTHONPATH python -m tests.manual.update_test_data -t {self.test_dir} --globus_token "" --offline_test --dry_run --verbose
                    """
        assert not diff, msg
        print(f"PASSED diff_test: {self.test_dir}")
        return diff


class UpdateFixtures:
    """
    Handles finding newest API responses, finding and printing diffs,
    and serializing/writing fixture data for LiveRunPersister and DryRunPersister.
    """

    def __init__(self, cassette_path: Path, cassette_dict: dict, serializer):
        self.cassette_path = cassette_path
        self.cassette_dict = cassette_dict
        self.serializer = serializer

    def get_diff(self, existing_data: dict, new_data: dict) -> bool:
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
            print(readable_diff(diff))
            return True
        else:
            print(f"No diff found for cassette {self.cassette_path}.")
            return False

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

    def get_new_data(self) -> dict:
        """
        In order to send all requests to endpoints when running in dry_run=False,
        we need to set record_mode="all" on vcr.OnlineTesting.my_vcr.
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
    """
    VCR class to determine what data to save when running in
    "live"/online mode. Prevents saving duplicate requests.
    """

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
    """
    VCR class to determine what data to save when running in
    "dry_run"/offline mode. Logs but saves no data.
    """

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


class IgnoreVersions(operator.BaseOperator):
    """
    DeepDiff class to ignore minor version changes to directory versions.
    """

    _patterns = (r"-v\d.\*", r"-v\d.\d")

    @classmethod
    def _remove_pattern(cls, pattern: str, t: str):
        return re.sub(pattern, "", t)

    def match(self, level):
        if re.search(self._patterns[0], str(level.t1)):
            return True

    def give_up_diffing(self, level, diff_instance):
        if re.search(self._patterns[0], str(level.t1)):
            t1 = self._remove_pattern(self._patterns[0], str(level.t1))
            t2 = self._remove_pattern(self._patterns[1], str(level.t2))
            return t1 == t2

    def normalize_value_for_hashing(self, _, obj):
        return obj
