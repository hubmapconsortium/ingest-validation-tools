import argparse
import glob
import json
from collections import defaultdict
from json.decoder import JSONDecodeError
from pathlib import Path

from deepdiff import DeepDiff

from ingest_validation_tools.cli_utils import dir_path
from ingest_validation_tools.error_report import ErrorDict, ErrorReport
from ingest_validation_tools.upload import Upload
from tests.test_dataset_examples import (
    DATASET_EXAMPLES_OPTS,
    DATASET_IEC_EXAMPLES_OPTS,
    PLUGIN_EXAMPLES_OPTS,
    MockException,
    TestDatasetExamples,
    check_report,
    diff_test,
)


class UpdateData:
    def __init__(
        self,
        dir: str,
        globus_token: str,
        exclude: list = [],
        opts: dict = {},
        verbose: bool = False,
        dry_run: bool = True,
        full_diff: bool = False,
    ):
        self.dir = dir if dir.endswith("/") else dir + "/"
        self.globus_token = globus_token
        self.exclude = exclude
        self.opts = opts if opts else DATASET_EXAMPLES_OPTS
        self.verbose = verbose
        self.upload_verbose = True if "plugin-tests" in dir else False
        self.dry_run = dry_run
        self.full_diff = full_diff

    def update_test_data(self) -> dict[str, list]:
        print(f"Evaluating {self.dir}...")
        self.change_report = defaultdict(list)
        upload = Upload(
            Path(f"{self.dir}upload"),
            globus_token=self.globus_token,
            verbose=self.upload_verbose,
            **self.opts,  # type: ignore
        )
        report = ErrorReport(upload)
        self.check_maybe_write_fixtures(report, upload)

        cleaned_report = check_report(report)
        self.check_maybe_write_readme(cleaned_report)

        return self.change_report

    ###################################
    #
    # fixtures.json methods
    #
    ###################################

    def open_or_create_fixtures(self) -> dict:
        if not Path(f"{self.dir}fixtures.json").exists():
            open(f"{self.dir}fixtures.json", "w")
        with open(f"{self.dir}fixtures.json", "r") as f:
            try:
                fixtures = json.load(f)
            except JSONDecodeError:
                fixtures = {}
        return fixtures

    def check_maybe_write_fixtures(self, report: ErrorReport, upload: Upload):
        if "fixtures" in self.exclude:
            print(f"{self.dir}fixtures.json excluded, not changed.")
        else:
            self.raise_or_print_fatal_errors(report)
            fixtures = self.open_or_create_fixtures()
            new_data = self.update_fixtures(upload)
            if self.fixtures_diff(fixtures, new_data) and not self.dry_run:
                print(f"Writing to {self.dir}fixtures.json...")
                with open(f"{self.dir}fixtures.json", "w") as f:
                    json.dump(new_data, f)

    def fixtures_diff(self, fixtures: dict, new_data: dict) -> bool:
        diff = DeepDiff(
            fixtures,
            new_data,
            ignore_order=True,
            report_repetition=True,
        )
        if not diff:
            print(f"No diff found, no update to {self.dir}fixtures.json...")
            return False
        elif self.dry_run:
            self.log(
                f"""
                    Diff:
                    {diff}

                    Would have written the following to {self.dir}fixtures.json:
                    {new_data}
                    """,
                short_message=f"Would have updated {self.dir}fixtures.json.",
            )
            self.change_report[self.dir].append("Fixtures diff found")
        return True

    def online_only_errors_by_path(self, path: str, upload_errors: ErrorDict):
        return upload_errors.errors_by_path(
            path,
            [
                upload_errors.metadata_url_errors,
                upload_errors.metadata_validation_api,
                upload_errors.metadata_constraint_errors,
            ],
        )

    def update_fixtures(self, upload: Upload) -> dict:
        """
        Collect soft assay endpoint / assay classifier response &
        online errors from ErrorDict (metadata_url_errors,
        metadata_validation_api, metadata_constraint_errors).
        """
        new_data = {}
        new_assaytype_data = {}
        new_validation_data = defaultdict(dict)
        for schema in upload.dataset_metadata.values():
            new_assaytype_data[schema.dataset_type] = schema.soft_assay_data
            online_errors = self.online_only_errors_by_path(str(schema.path), upload.errors)
            new_validation_data[schema.schema_name].update(online_errors)
            for supporting_schema in [
                *schema.contributors_schemas,
                *schema.antibodies_schemas,
            ]:
                online_errors = self.online_only_errors_by_path(
                    str(supporting_schema.path), upload.errors
                )
                new_validation_data[supporting_schema.schema_name].update(online_errors)
        new_data["assaytype"] = new_assaytype_data
        new_data["validation"] = dict(new_validation_data)
        return new_data

    ###################################
    #
    # README.json methods
    #
    ###################################

    def open_or_create_readme(self) -> dict:
        if not Path(f"{self.dir}README.json").exists():
            with open(f"{self.dir}README.json", "w") as f:
                json.dump({}, f)
        with open(f"{self.dir}README.json", "r") as f:
            return json.load(f)

    def check_maybe_write_readme(self, cleaned_report: ErrorReport):
        """
        Check existing readme against new ErrorReport.
        If there is a difference, write new readme.
        """
        if "README" in self.exclude:
            print(f"{self.dir}README.json excluded, not changed.")
        else:
            readme = self.open_or_create_readme()
            if self.readme_diff(readme, cleaned_report):
                self.write_readme(cleaned_report)

    def write_readme(self, cleaned_report: ErrorReport):
        if cleaned_report.errors:
            report = cleaned_report.errors
        else:
            cleaned_report.raw_info.time = "WILL_CHANGE"
            cleaned_report.raw_info.git = "WILL_CHANGE"
            report = cleaned_report.raw_info.as_dict()
        if self.dry_run:
            self.log(
                f"""
                    Would have written the following report to {self.dir}README.json:
                    {report}
                    """,
                f"Would have updated {self.dir}README.json.",
            )
            self.change_report[self.dir].append("README diff found")
        else:
            self.log(
                f"""
                    Writing the following report to {self.dir}README.json:
                    {report}
                    """,
                f"Updating {self.dir}README.json.",
            )
            with open(f"{self.dir}README.json", "w") as f:
                json.dump(report, f)

    def readme_diff(self, readme, cleaned_report: ErrorReport) -> bool:
        try:
            diff_test(
                self.dir,
                readme,
                cleaned_report,
                verbose=self.verbose,
            )
            print(f"No diff found, no update to {self.dir}README.json")
        except MockException:
            print("Expected exception found for test, continuing.")
        except AssertionError as e:
            print(f"FAILED diff_test: {self.dir}README.json")
            if str(e):
                print(str(e))
            return True
        return False

    ###################################
    #
    # Helper methods
    #
    ###################################

    def log(self, verbose_message, short_message: str | None = None):
        if self.verbose:
            print(verbose_message)
        elif short_message:
            print(short_message)

    def raise_or_print_fatal_errors(self, report: ErrorReport):
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
            if error in report.as_md():
                # Necessary to avoid including 'Unauthorized' in output when no Globus token is provided,
                # but only relevant for entity-api links
                if error in ["Unauthorized for url: https://entity.api", "No token"]:
                    msg = f"URL checking returned 'Unauthorized' in response while checking {self.dir}; did you forget a Globus token?"
                else:
                    msg = f"Something went wrong with Spreadsheet Validator request for {self.dir}: {error}"
                if not self.dry_run:
                    raise Exception(msg)
                print(f"Error checking {self.dir}: {msg}.")


def print_change_report(change_report: dict, verbose: bool, globus_token: str):
    if change_report:
        print("-------CHANGE REPORT-------")
        if verbose:
            for dir, messages in change_report.items():
                print(f"{dir}: {', '.join([msg for msg in messages])}")
            print(
                f"""
                To update all, run:
                env PYTHONPATH=/ingest-validation-tools python -m tests.online.update_test_data -t {' '.join([dir for dir in change_report.keys()])} --globus_token {globus_token} --verbose
                """
            )
        else:
            print("Dirs with errors:")
            for dir, _ in change_report.items():
                print(dir)


def offline_test(test_dir: str | list, verbose: bool = False):
    """
    Offline test (mimics unittest behavior) at the level of a
    single directory.
    """
    if type(test_dir) is str:
        assert Path(
            test_dir
        ).resolve(), f"Arg {test_dir} passed to offline_test is not a directory!"
    elif type(test_dir) is list and len(test_dir) > 1:
        test_dir = [dir for dir in test_dir if Path(dir).is_dir()]
    test = TestDatasetExamples()
    setattr(test, "dataset_test_dirs", test_dir)
    test.get_paths()
    test.test_validate_dataset_examples(verbose=verbose)


def get_opts(dir: str):
    if "dataset-examples" in dir:
        opts = DATASET_EXAMPLES_OPTS
    elif "dataset-iec-examples" in dir:
        opts = DATASET_IEC_EXAMPLES_OPTS
    elif "plugin-tests" in dir:
        opts = PLUGIN_EXAMPLES_OPTS
    else:
        opts = {}
    return opts


def call_update(dir: str, args) -> dict:
    change_report = UpdateData(
        dir,
        args.globus_token,
        opts=get_opts(dir),
        dry_run=args.dry_run,
        verbose=args.verbose,
        exclude=args.exclude,
        full_diff=args.full_diff,
    ).update_test_data()
    return change_report


parser = argparse.ArgumentParser(
    description="Update README.json and fixtures.json files for a given example directory by passing the directory name (the parent of the upload directory) and a Globus token."
)
parser.add_argument(
    "-t",
    "--target_dirs",
    help="""
    [Required] The directory or directories containing the target README.json and fixtures.json files to update. Can pass multiple directories, e.g. '-t examples/dataset-examples/a examples/dataset-examples/b'.
    Can also specify the following example directories to update all examples in each: 'examples/dataset-examples', 'examples/dataset-iec-examples', 'examples/plugin-tests'. Pass all with:
    -t examples/dataset-examples examples/dataset-iec-examples examples/plugin-tests
    """,
    nargs="+",
    required=True,
    type=dir_path,
)
parser.add_argument(
    "-g",
    "--globus_token",
    help="[Optional for offline_test] Token obtained from Globus, e.g. can be found in the Authorization header when you are logged in to Ingest UI. Omit 'Bearer' portion.",
    required=True,
    type=str,
)
parser.add_argument(
    "-d",
    "--dry_run",
    action="store_true",
    help="[Optional] Default is False. If specified, do not write data but instead print output.",
)
parser.add_argument(
    "-v",
    "--verbose",
    action="store_true",
    help="[Optional] Default is False. If specified, prints more verbose output.",
)
parser.add_argument(
    "-e",
    "--exclude",
    choices=["README", "fixtures"],
    default=[],
    help="[Optional] Specify if you want to skip writing either README or fixtures. Can only accept one argument; use --dry_run instead if you want to preview output.",
)
parser.add_argument(
    "-o",
    "--offline_test",
    action="store_true",
    help="[Optional] Default is False. Used for investigating testing failures with more verbose output. Requires passing a test_dir. Pass a blank Globus token as this runs offline.",
)
parser.add_argument(
    "-f",
    "--full_diff",
    action="store_true",
    help="[Optional] Default is False. Show full and cleaned README diff.",
)
parser.add_argument(
    "-i",
    "--ignore_online_exceptions",
    action="store_true",
    help="[Optional] Default is False. Print 'Too Many Requests' (Spreadsheet Validator error) and 'Unauthorized' (Globus token error) exceptions rather than raising.",
)
parser.add_argument(
    "--start_index",
    type=int,
    default=0,
    help="[Optional] Choose a test dir index to start at, skipping prior indices; used when testing is interrupted.",
)

args = parser.parse_args()


parent_dirs = [
    "examples/dataset-examples",
    "examples/dataset-iec-examples",
    "examples/plugin-tests",
]


def get_sub_dirs(target_dir: str) -> list[str]:
    if Path(target_dir).absolute() in [Path(path).absolute() for path in parent_dirs]:
        sub_dirs = [
            example_dir
            for example_dir in glob.glob(f"{target_dir}/**")
            if Path(example_dir).is_dir()
        ]
        return sorted(sub_dirs)
    return [target_dir]


def run_offline_tests(target_dirs: list, args):
    sub_dirs = []
    if target_dirs in [["examples/"], ["examples"]]:
        target_dirs = parent_dirs
    for dir in target_dirs:
        sub_dirs.extend(get_sub_dirs(dir))
    for index, sub_dir in enumerate(sub_dirs):
        if args.start_index and index < args.start_index:
            print(f"Skipping {index}: {sub_dir}")
            continue
        print(f"{index}: {sub_dir}")
        offline_test([sub_dir], verbose=args.verbose)


def run_update(target_dirs: list, args):
    change_report = {}
    if target_dirs in [["examples/"], ["examples"]]:
        target_dirs = parent_dirs
    for dir in target_dirs:
        sub_dirs = get_sub_dirs(dir)
        for sub_dir in sub_dirs:
            change_report.update(call_update(str(sub_dir), args))
    return change_report


if args.offline_test:
    run_offline_tests(args.target_dirs, args)
else:
    change_report = run_update(args.target_dirs, args)
    print_change_report(change_report, verbose=args.verbose, globus_token=args.globus_token)
