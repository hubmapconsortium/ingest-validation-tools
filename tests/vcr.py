import glob
import re
from pathlib import Path

from vcr import VCR
from vcr.request import Request
from vcr.unittest import VCRTestCase

from ingest_validation_tools.upload import Upload
from tests.vcr_utils import DryRunPersister, LivePersister

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


def create_upload(dataset_path: str, globus_token: str) -> Upload:
    if "dataset-examples" in dataset_path:
        opts = DATASET_EXAMPLES_OPTS
    elif "dataset-iec-examples" in dataset_path:
        opts = DATASET_IEC_EXAMPLES_OPTS
    elif "plugin-tests" in dataset_path:
        opts = PLUGIN_EXAMPLES_OPTS
    else:
        opts = {}
    return Upload(Path(f"{dataset_path}/upload"), globus_token=globus_token, **opts)


class LiveTesting:
    def __init__(
        self,
        paths: list[str],
        globus_token: str,
        dry_run=False,
    ):
        self.paths = paths
        # dry_run=False runs live tests and updates fixtures
        # dry_run=True runs live tests and prints updates
        self.dry_run = dry_run
        self.globus_token = globus_token
        self.responses = {}
        self.live_tests()
        self.current_cassette = None

    def before_record_request(self, request):
        new_headers = {}
        new_headers["Authorization"] = "Bearer xxxxxxx"
        new_headers["Content-Type"] = request.headers.get("Content-Type")
        replace_str = re.search(r"; boundary=(.*)", request.headers.get("Content-Type", ""))
        body = request.body.decode("utf-8")
        if replace_str and len(replace_str.groups()) == 1:
            sub_str = replace_str.groups()[0]
            body = body.replace(sub_str, "")
        new_request = Request(request.method, request.uri, body, new_headers)
        if self.dry_run:
            return None
        return new_request

    def before_record_response(self, response):
        response["headers"] = {}
        if isinstance(response.get("body", {}).get("string"), bytes):
            response["body"]["string"] = response["body"]["string"].decode("utf-8")
        if self.dry_run:
            return None
        return response

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
            my_vcr.register_persister(LivePersister)
        return my_vcr

    def live_test(self, path: str, record_mode: str):
        with self.my_vcr.use_cassette(
            Path(path) / "fixtures.json",
            record_mode=record_mode,
            decode_compressed_response=True,
            match_on=["body"],
        ) as cassette:  # type: ignore
            print(f"Testing {path}...")
            upload = create_upload(path, self.globus_token)
            upload.get_errors()
            readme = open(f"{path}README.md", "r")
            # Diff report & readme
            # If diff and not dry_run:
            #   Write report to README
            # If not diff:
            #   Pass, log

    def live_tests(self):
        for path in self.paths:
            if self.dry_run:
                record_mode = "none"
            else:
                record_mode = "all"
            self.live_test(path, record_mode)


class MyTestCase(VCRTestCase):

    dataset_test_dirs = [
        test_dir
        for test_dir in [
            *glob.glob("examples/dataset-examples/**"),
            *glob.glob("examples/dataset-iec-examples/**"),
        ]
        if Path(test_dir).is_dir()
    ]

    def _get_vcr(self, **kwargs):
        kwargs["cassette_library_dir"] = f"{kwargs.get('test_dir')}/fixtures.json"
        return VCR(**kwargs)

    def get_paths(self):
        # TODO: default to all in examples/dataset-examples and examples/dataset-iec-examples
        dataset_paths = {}
        for test_dir in self.dataset_test_dirs:
            metadata_paths = [path for path in Path(f"{test_dir}/upload").glob("*metadata.tsv")]
            dataset_paths[test_dir] = metadata_paths
        return dataset_paths

    def test_dataset_examples(self):
        for test_dir in self.get_paths():
            print(f"Testing {test_dir}...")
            with self.cassette(cassette_library_dir=test_dir):
                upload = create_upload(test_dir, "")
                upload.get_errors()
            readme = open(f"{test_dir}/README.md", "r")
            # Diff report & readme
            # If not diff:
            #   Pass, log
