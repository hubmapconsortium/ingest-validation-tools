import unittest
from pathlib import Path

from vcr import VCR
from vcr.unittest import VCRTestCase

from tests.vcr_utils import vcr_create_upload_and_diff


def get_paths(test_dirs: list[Path]):
    dataset_paths = {}
    for test_dir in test_dirs:
        metadata_paths = [path for path in Path(f"{test_dir}/upload").glob("*metadata.tsv")]
        dataset_paths[test_dir] = metadata_paths
    return dataset_paths


def test_dataset_examples(test_dirs: list[Path]):
    """
    Test example dataset directories using fixture cassettes.
    """
    change_report = {}
    for test_dir in get_paths(test_dirs):
        print(f"Testing {test_dir}...")
        if not (Path(test_dir) / "fixtures.json").exists():
            raise Exception("New fixture data required, run ")  # TODO
        report = vcr_create_upload_and_diff(
            test_dir, globus_token="offline_test", record_mode="none"
        )
        change_report[test_dir] = report
    print_change_report(change_report)


def print_change_report(change_report: dict[str, str], verbose: bool = True):
    if change_report:
        print("-------CHANGE REPORT-------")
        if verbose:
            for dir, message in change_report.items():
                print(f"{dir}: {message}")
            # TODO
            print(
                f"""
                To update all, run: TODO
                """
            )
        else:
            print("Dirs with errors:")
            for dir, _ in change_report.items():
                print(dir)


class TestSpecificExamples:
    """
    Manually specify a list of dirs to test.
    Runs offline. To run online tests and/or update fixture data,
    use vcr_utils.py > OnlineTesting
    """

    def __init__(self, test_dirs: list[Path | str]):
        self.test_dirs = [Path(dir) for dir in test_dirs]
        test_dataset_examples(self.test_dirs)


class TestDatasetExamples(unittest.TestCase):
    """
    Test all directories in examples/.
    """

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

    def test_dataset_examples(self):
        test_dataset_examples(self.dataset_test_dirs)


class MyTestCase(VCRTestCase):

    def _get_vcr(self, **kwargs):
        kwargs["cassette_library_dir"] = f"{kwargs.get('test_dir')}/fixtures.json"
        return VCR(**kwargs)
