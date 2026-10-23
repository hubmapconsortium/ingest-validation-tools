import glob
from datetime import datetime
from pathlib import Path

from vcr.unittest import VCRTestCase

from ingest_validation_tools.upload import Upload
from tests.fixtures.fixtures import PLUGIN_INFO
from tests.test_dataset_examples import (
    PLUGIN_EXAMPLES_OPTS,
    TestExamples,
)


class TestPluginExamples(VCRTestCase):

    dataset_test_dirs = [
        test_dir
        for test_dir in [
            *glob.glob("examples/plugin-tests/**"),
        ]
        if Path(test_dir).is_dir()
    ]

    def test_info_reporting(self):
        fake_now = datetime.now()
        for test_dir in glob.glob("examples/plugin-tests/**"):
            upload = Upload(
                Path(f"{test_dir}/upload"), **PLUGIN_EXAMPLES_OPTS, verbose=False
            )  # Can flip to True if debugging
            upload.get_errors()
            info = upload.get_info()
            if info is None:
                raise Exception("Info should not be none.")
            assert info.git
            assert info.time
            info.git = "WILL_CHANGE"
            info.time = fake_now
            info_dict = PLUGIN_INFO[Path(test_dir).absolute()]
            info_dict.time = fake_now
            self.assertEqual(info_dict, info)

    def test_validate_dataset_examples(self, verbose: bool = False, full_diff: bool = False):
        super().test_validate_dataset_examples()
