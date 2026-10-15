from pathlib import Path

from vcr import VCR, use_cassette
from vcr.unittest import VCRTestCase

from tests.vcr_utils import create_upload


class MyTestCase(VCRTestCase):

    @property
    def dataset_test_dirs(self):
        # TODO: fix
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
