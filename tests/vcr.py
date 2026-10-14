from datetime import datetime
from pathlib import Path

from vcr import VCR, use_cassette
from vcr.request import Request
from vcr.unittest import VCRTestCase

from ingest_validation_tools.upload import Upload
from tests.vcr_utils import DATETIME_FORMAT, DryRunPersister, LiveRunPersister

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


class MyTestCase(VCRTestCase):

    @property
    def dataset_test_dirs(self):
        return [
            Path("examples/dataset-examples/good-cedar-histology")
            # test_dir
            # for test_dir in [
            #     *glob.glob("examples/dataset-examples/**"),
            #     *glob.glob("examples/dataset-iec-examples/**"),
            # ]
            # if Path(test_dir).is_dir()
        ]

    def _get_vcr(self, **kwargs):
        kwargs["cassette_library_dir"] = f"{kwargs.get('test_dir')}/fixtures.json"
        kwargs["drop_unused_requests"] = True
        return VCR(**kwargs)

    def get_paths(self):
        # TODO: specify dirs
        dataset_paths = {}
        for test_dir in self.dataset_test_dirs:
            metadata_paths = [path for path in Path(f"{test_dir}/upload").glob("*metadata.tsv")]
            dataset_paths[test_dir] = metadata_paths
        return dataset_paths

    def test_dataset_examples(self):
        for test_dir in self.get_paths():
            print(f"Testing {test_dir}...")
            if not (Path(test_dir) / "fixtures.json").exists():
                raise Exception("New fixture data required, run ")  # TODO
            with use_cassette(Path(test_dir) / "fixtures.json"):
                upload = create_upload(test_dir, "offline_test")
                upload.get_errors()
            readme = open(Path(test_dir) / "README.json")
            readme.close()
            # Diff report & readme
            # If not diff:
            #   Pass, log
