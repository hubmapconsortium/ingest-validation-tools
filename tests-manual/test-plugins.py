import glob
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from ingest_validation_tools.upload import Upload
from tests.fixtures import PLUGIN_DIR_MAP
from tests.test_dataset_examples import PLUGIN_EXAMPLES_OPTS, assaytype_side_effect


class TestPlugins(unittest.TestCase):
    def test_info_reporting(self):
        with patch(
            "ingest_validation_tools.validation_utils.get_assaytype_data",
            side_effect=lambda row, ingest_url: assaytype_side_effect(test_dir, row, ingest_url),
        ):
            with patch("ingest_validation_tools.upload.Upload.online_checks"):
                fake_now = datetime.now()
                for test_dir in glob.glob(f"examples/plugin-tests/**"):
                    upload = Upload(
                        Path(f"{test_dir}/upload"), **PLUGIN_EXAMPLES_OPTS, verbose=False
                    )
                    upload.get_errors()
                    info = upload.get_info()
                    if info is None:
                        raise Exception("Info should not be none.")
                    assert info.git
                    assert info.time
                    info.git = "WILL_CHANGE"
                    info.time = fake_now
                    info_dict = PLUGIN_DIR_MAP[Path(test_dir).absolute()]
                    info_dict.time = fake_now
                    self.assertEqual(info_dict, info)
