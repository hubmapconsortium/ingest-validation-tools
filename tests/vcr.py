import glob
from pathlib import Path

from vcr import VCR
from vcr.unittest import VCRTestCase

from ingest_validation_tools.upload import Upload

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
        self.dry_run = dry_run
        self.globus_token = globus_token
        self.responses = {}
        self.live_tests()

    def before_record_request(self, request, **kwargs):
        if kwargs.get("dry_run"):
            return None
        return request

    def before_record_response(self, response, **kwargs):
        # TODO: not sure if this needs to return a callable
        self.responses[kwargs.get("test_dir")] = response
        # TODO: compare? don't care much about the data but good to know when fixture is changing / would change
        if kwargs.get("dry_run"):
            return None
        return response

    @property
    def my_vcr(self):
        return VCR(
            record_on_exception=False,
            before_record_request=self.before_record_request({"dry_run": self.dry_run}),
            before_record_response=self.before_record_response({"dry_run": self.dry_run}),
        )

    def test_factory(self, path: str):
        @self.my_vcr.use_cassette(f"{path}/fixtures.yaml", record_mode="all")
        def live_test():
            print(f"Testing {path}...")
            upload = create_upload(path, self.globus_token)
            upload.get_errors()
            readme = open(f"{path}/README.md", "r")
            # Diff report & readme
            # If diff and not dry_run:
            #   Write report to README
            # If not diff:
            #   Pass, log

        return live_test

    def live_tests(self):
        for path in self.paths:
            self.test_factory(path)()


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
        kwargs["cassette_library_dir"] = f"{kwargs.get('test_dir')}/fixtures.yaml"
        return VCR(**kwargs)

    def get_paths(self):
        # TODO: default to all in examples/dataset-examples and examples/dataset-iec-examples
        dataset_paths = {}
        for test_dir in self.dataset_test_dirs:
            metadata_paths = [path for path in Path(f"{test_dir}/upload").glob("*metadata.tsv")]
            dataset_paths[test_dir] = metadata_paths
        return dataset_paths

    def test_dataset_examples(self):
        test_dirs = self.get_paths()
        for test_dir in test_dirs:
            print(f"Testing {test_dir}...")
            with self.cassette(cassette_library_dir=test_dir):
                upload = create_upload(test_dir, "")
                upload.get_errors()
            readme = open(f"{test_dir}/README.md", "r")
            # Diff report & readme
            # If not diff:
            #   Pass, log
