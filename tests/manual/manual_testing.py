import argparse
from pathlib import Path

from vcr import VCR
from vcr.request import Request

from ingest_validation_tools.cli_utils import dir_path
from tests.manual.updaters import LiveRunPersister
from tests.utils import (
    default_before_record_request,
    default_before_record_response,
    get_example_paths,
    prepare_change_report,
    test_dataset_examples,
    vcr_create_upload_and_diff,
)


def test_specific_examples(test_dirs: list[Path], verbose: bool = False, dry_run: bool = True):
    """
    Manually specify a list of dirs to test.
    Runs offline. To run online tests and/or update fixture data,
    use vcr_utils.py > OnlineTesting.
    Specify dry_run=False to update readme files from fixtures.
    See tests/README.md for command line usage.
    """
    test_dir_paths = [Path(dir) for dir in test_dirs]
    report = test_dataset_examples(test_dir_paths, dry_run=dry_run, verbose=verbose)
    if report:
        print("\n".join(prepare_change_report(report)))


class OnlineTesting:
    """
    Run tests with live API calls, re-record results
    to fixtures.json files (destructive--deletes and recreates file).
    Fails if fatal errors are encountered.
    See tests/README.md for command line usage.
    """

    def __init__(
        self,
        globus_token: str,
        dry_run: bool = False,
        paths: list[Path] | None = None,
        verbose: bool = False,
    ):
        """
        Arguments:
            globus_token: Globus API token
            paths: (optional) list of example dir paths to test;
                    default behavior tests all
            dry_run:
                False: overwrite README.json if changed
                True: print prospective changes to README.json
            verbose: print more detailed messages
        """
        self.paths = self.get_paths(paths)
        self.globus_token = globus_token
        self.dry_run = dry_run
        self.verbose = verbose
        self.live_tests()

    def get_paths(self, paths: list[Path] | None) -> list:
        if paths:
            return [Path(path) for path in paths]
        else:
            return get_example_paths()

    def before_record_request(self, request: Request) -> Request:
        return default_before_record_request(request)

    def before_record_response(self, response: dict) -> dict:
        return default_before_record_response(response)

    @property
    def my_vcr(self) -> VCR:
        my_vcr = VCR(
            before_record_request=self.before_record_request,
            before_record_response=self.before_record_response,
            serializer="json",
        )
        my_vcr.register_persister(LiveRunPersister)
        return my_vcr

    def live_tests(self):
        report = []
        for path in self.paths:
            print(f"Testing {path}...")
            diff = vcr_create_upload_and_diff(
                path, self.globus_token, record_mode="all", vcr=self.my_vcr, dry_run=self.dry_run
            )
            if diff:
                report.append(diff)
        print("\n".join(report))


parser = argparse.ArgumentParser(
    description="Update README.json and fixtures.json files for a given example directory by passing the directory name (the parent of the upload directory) and a Globus token."
)

parser.add_argument(
    "-t",
    "--target_dirs",
    help="""
    [Required] The directory or directories containing the target README.json and fixtures.json files to update. Can pass multiple directories, e.g. '-t examples/dataset-examples/a examples/dataset-examples/b'.
    Can also specify the following example directories to update all examples in each: 'examples/dataset-examples', 'examples/dataset-iec-examples', 'examples/plugin-tests'. Pass all with:
    -t examples/
    """,
    nargs="+",
    type=dir_path,
)
parser.add_argument(
    "-w",
    "--write_readmes",
    action="store_true",
    help="[Optional] Default is False. If specified, will write data to README.json files.",
)
parser.add_argument(
    "-o",
    "--online",
    action="store_true",
    help="[Optional] Default is False. If specified, will make live API calls and overwrite fixture data.",
)
parser.add_argument(
    "-g",
    "--globus_token",
    help="[Required if --online is passed] Token obtained from Globus, e.g. can be found in the Authorization header when you are logged in to Ingest UI. Omit 'Bearer' portion.",
    type=str,
)
parser.add_argument(
    "-v",
    "--verbose",
    action="store_true",
    help="[Optional] Default is False. If specified, prints more verbose output.",
)

args = parser.parse_args()
dry_run = False if args.write_readmes else True
if not args.online:
    test_specific_examples(
        [Path(dir) for dir in args.target_dirs] if args.target_dirs else get_example_paths(),
        dry_run=dry_run,
        verbose=args.verbose,
    )
else:
    OnlineTesting(
        args.globus_token,
        dry_run,
        paths=[Path(dir) for dir in args.target_dirs] if args.target_dirs else get_example_paths(),
        verbose=args.verbose,
    )
