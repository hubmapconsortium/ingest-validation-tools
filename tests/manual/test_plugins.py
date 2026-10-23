import argparse
import glob
import sys
import unittest
from pathlib import Path

from vcr.unittest import VCRTestCase

from ingest_validation_tools.upload import Upload
from tests.manual.updaters import remove_minor_version
from tests.utils import (
    PLUGIN_EXAMPLES_OPTS,
    default_before_record_request,
    default_before_record_response,
    prepare_change_report,
    test_dataset_examples,
    validation_matcher,
)

TOKEN = "test_plugins_token"


class TestPluginExamples(VCRTestCase):

    def _get_vcr(self, **kwargs):
        kwargs["before_record_request"] = default_before_record_request
        kwargs["before_record_response"] = default_before_record_response
        kwargs["cassette_library_dir"] = "tests/fixtures/cassettes"
        myvcr = super(TestPluginExamples, self)._get_vcr(**kwargs)
        myvcr.register_matcher("validation_matcher", validation_matcher)
        myvcr.match_on = ["validation_matcher"]
        return myvcr

    dataset_test_dirs = [
        Path(test_dir)
        for test_dir in [
            *glob.glob("examples/plugin-tests/**"),
        ]
        if Path(test_dir).is_dir()
    ]

    @property
    def get_plugin_example_opts(self):
        return PLUGIN_EXAMPLES_OPTS | {"globus_token": TOKEN}

    def test_info_reporting(self):
        info_dict_data = {
            "examples/plugin-tests/prev-gen-codex-expected-failure": {
                "tsvs": {
                    "name-just-needs-to-end-with-metadata.tsv": {
                        "Metadata type": "codex-v1",
                        "Metadata version": "1",
                        "Directory schema version": "codex-v1.*",
                    }
                },
                "successful_plugins": ["CodexCommonErrorsValidator"],
            },
            "examples/plugin-tests/expected-failure": {
                "tsvs": {
                    "good-visium-assay-metadata.tsv": {
                        "Metadata type": "Visium (no probes)",
                        "Metadata version": "babf1e69-f0eb-479a-bdc5-b70199669675",
                        "Directory schema version": "visium-no-probes-v3.*",
                    },
                    "good-visium-histology-metadata.tsv": {
                        "Metadata type": "Histology",
                        "Metadata version": "e7475329-9a60-4088-8e34-19a3828e0b3b",
                        "Directory schema version": "visium-no-probes-v3.*",
                    },
                    "good-visium-rnaseq-metadata.tsv": {
                        "Metadata type": "RNAseq",
                        "Metadata version": "944e5fa0-f68b-4bdd-8664-74a3909429a9",
                        "Directory schema version": "visium-no-probes-v3.*",
                    },
                },
                "successful_plugins": ["GZValidator"],
            },
        }
        for test_dir in self.dataset_test_dirs:
            upload = Upload(test_dir / "upload", **self.get_plugin_example_opts)
            upload.get_errors()
            upload_info = upload.get_info()
            breakpoint()
            assert upload_info.git
            assert upload_info.time
            for tsv in upload_info.tsvs.keys():
                dir_schema_version = upload_info.tsvs[tsv].get("Directory schema version")
                if dir_schema_version:
                    upload_info.tsvs[tsv]["Directory schema version"] = remove_minor_version(
                        dir_schema_version
                    )
            assert upload_info.tsvs == info_dict_data[str(test_dir)]["tsvs"]
            assert (
                upload_info.successful_plugins
                == info_dict_data[str(test_dir)]["successful_plugins"]
            )

    def test_dataset_examples(self):
        """
        Automatically runs plugin tests due to dir name matching in utils.create_upload.
        """
        errors = test_dataset_examples(self.dataset_test_dirs, globus_token=TOKEN)
        assert not errors, "\n".join(prepare_change_report(errors))


if __name__ == "__main__":
    """
    Example usage:
        python tests/test_plugin_examples.py -t <globus_token>
    """
    parser = argparse.ArgumentParser(
        description="Pass HuBMAP Globus token to update fixture cassettes (must delete previous cassette) from tests/fixtures/cassettes"
    )
    parser.add_argument("-t", "--token")
    parser.add_argument("unittest_args", nargs="*")

    args = parser.parse_args()

    if args.token:
        TOKEN = args.token
    sys.argv[1:] = args.unittest_args
    unittest.main()
