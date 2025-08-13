import argparse
import glob
import json
from collections import defaultdict
from json.decoder import JSONDecodeError
from pathlib import Path
from typing import Dict, List, Optional, Union

from deepdiff import DeepDiff

from ingest_validation_tools.cli_utils import dir_path
from ingest_validation_tools.error_report import ErrorReport
from ingest_validation_tools.upload import Upload
from tests.test_dataset_examples import (
    DATASET_EXAMPLES_OPTS,
    DATASET_IEC_EXAMPLES_OPTS,
    PLUGIN_EXAMPLES_OPTS,
    MockException,
    TestDatasetExamples,
    TokenException,
    clean_report,
    dataset_test,
    dev_url_replace,
    diff_test,
    get_non_token_errors,
)


class UpdateData:
    def __init__(
        self,
        dir: str,
        globus_token: str,
        exclude: List = [],
        opts: Dict = {},
        verbose: bool = False,
        dry_run: bool = True,
        full_diff: bool = False,
        update_from_fixtures: bool = False,
        ignore_online_exceptions: bool = False,
        env: str = "PROD",
    ):
        self.dir = dir if dir.endswith("/") else dir + "/"
        self.globus_token = globus_token
        self.exclude = exclude
        self.opts = opts if opts else DATASET_EXAMPLES_OPTS
        self.verbose = verbose
        self.upload_verbose = True if "plugin-tests" in dir else False
        self.dry_run = dry_run
        self.full_diff = full_diff
        self.update_from_fixtures = update_from_fixtures
        self.ignore_online_exceptions = ignore_online_exceptions
        self.env = env

    def update_test_data(self) -> Dict[str, List]:
        print(f"Evaluating {self.dir}...")
        self.change_report = defaultdict(list)
        if self.update_from_fixtures:
            upload = TestDatasetExamples.prep_offline_upload(self.dir, self.opts)
            report = ErrorReport(errors=upload.errors, info=upload.info)
        else:
            upload = Upload(
                Path(f"{self.dir}upload"),
                globus_token=self.globus_token,
                verbose=self.upload_verbose,
                **self.opts,  # type: ignore
            )
        report = ErrorReport(upload)
        self.check_maybe_write_fixtures(report, upload)

        try:
            cleaned_report = clean_report(report)
        except TokenException as e:
            if self.ignore_online_exceptions:
                print(e)
                assert (
                    type(e.clean_report) is str
                ), f"TokenException returned wrong data type for clean_report, check or try passing Globus token. clean_report type: {type(clean_report)}, value: {clean_report}"
                cleaned_report = e.clean_report
            else:
                raise TokenException(str(e), e.clean_report)
        self.check_maybe_write_readme(cleaned_report)

        return self.change_report

    ###################################
    #
    # fixtures.json methods
    #
    ###################################

    def open_or_create_fixtures(self) -> Dict:
        if not Path(f"{self.dir}fixtures.json").exists():
            open(f"{self.dir}fixtures.json", "w")
        with open(f"{self.dir}fixtures.json", "r") as f:
            try:
                fixtures = json.load(f)
            except JSONDecodeError:
                fixtures = {}
        return fixtures

    def check_maybe_write_fixtures(self, report: ErrorReport, upload: Upload):
        if self.update_from_fixtures:
            print(f"Updating from fixture data, fixtures not changed for {self.dir}.")
        elif "fixtures" in self.exclude:
            print(f"{self.dir}fixtures.json excluded, not changed.")
        else:
            self.raise_or_print_fatal_errors(report)
            fixtures = self.open_or_create_fixtures()
            try:
                new_data = self.update_fixtures(upload)
            except TokenException as e:
                self.dry_run = True
                print(e)
                new_data = e.clean_report
            assert (
                type(new_data) is dict
            ), f"TokenException returned wrong data type for new_data, check or try passing Globus token. new_data type: {type(new_data)}, value: {new_data}"
            if self.env == "DEV":
                new_data = self.get_dev_env_data(new_data)
            if self.fixtures_diff(fixtures, new_data) and not self.dry_run:
                print(f"Writing to {self.dir}fixtures.json...")
                with open(f"{self.dir}fixtures.json", "w") as f:
                    json.dump(new_data, f)

    def fixtures_diff(self, fixtures: Dict, new_data: Dict) -> bool:
        diff = DeepDiff(
            fixtures,
            new_data,
            ignore_order=True,
            report_repetition=True,
        )
        if not diff:
            print(f"No diff found, skipping {self.dir}fixtures.json...")
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

    def update_fixtures(self, upload) -> Dict:
        new_data = {}
        new_assaytype_data = {}
        new_validation_data = defaultdict(dict)
        no_token_error = False
        for schema in upload.dataset_metadata.values():
            new_assaytype_data[schema.dataset_type] = schema.soft_assay_data
            if upload.errors.metadata_url_errors:
                upload.errors = get_non_token_errors(upload.errors)
            online_errors = upload.errors.online_only_errors_by_path(str(schema.path))
            new_validation_data[schema.schema_name].update(online_errors)
            antibodies_paths = set()
            contributors_paths = set()
            for row in schema.rows:
                if antibodies_path := row.get("antibodies_path"):
                    antibodies_paths.add(antibodies_path)
                if contributors_path := row.get("contributors_path"):
                    contributors_paths.add(contributors_path)
            for other_type, paths in {
                "antibodies": antibodies_paths,
                "contributors": contributors_paths,
            }.items():
                for path in paths:
                    online_errors = upload.errors.online_only_errors_by_path(path)
                    new_validation_data[other_type].update(online_errors)
        new_data["assaytype"] = new_assaytype_data
        new_data["validation"] = dict(new_validation_data)
        if no_token_error:
            raise TokenException("No token passed, cannot update fixtures", new_data)
        return new_data

    ###################################
    #
    # README.md methods
    #
    ###################################

    def open_or_create_readme(self):
        if not Path(f"{self.dir}README.md").exists():
            open(f"{self.dir}README.md", "w")
        return open(f"{self.dir}README.md", "r")

    def check_maybe_write_readme(self, cleaned_report: str):
        if "README" in self.exclude:
            print(f"{self.dir}README.md excluded, not changed.")
        else:
            readme = self.open_or_create_readme()
            if self.readme_diff(readme, cleaned_report):
                self.write_readme(cleaned_report)
                if not self.dry_run:
                    dataset_test(
                        self.dir,
                        self.opts,
                        globus_token=self.globus_token,
                        offline=self.update_from_fixtures,
                        use_online_check_fixtures=self.update_from_fixtures,
                    )

    def write_readme(self, cleaned_report: str):
        if self.dry_run or self.ignore_online_exceptions:
            self.log(
                f"""
                    Would have written the following report to {self.dir}README.md:
                    {cleaned_report}
                    """,
                f"Would have updated {self.dir}README.md.",
            )
            self.change_report[self.dir].append("README diff found")
        else:
            self.log(
                f"""
                    Writing the following report to {self.dir}README.md:
                    {cleaned_report}
                    """,
                f"Updating {self.dir}README.md.",
            )
            with open(f"{self.dir}README.md", "w") as f:
                f.write(cleaned_report)

    def readme_diff(self, readme, cleaned_report: str) -> bool:
        try:
            diff_test(
                self.dir,
                readme,
                cleaned_report,
                verbose=self.verbose,
                full_diff=self.full_diff,
                env=self.env,
            )
            readme.close()
            print(f"No diff found, skipping {self.dir}README.md")
        except MockException:
            print("Expected exception found for test, continuing.")
        except TokenException as e:
            print(f"Token error for {self.dir}README.md. Non-token-related diff: {e.clean_report}")
        except AssertionError:
            print(f"FAILED diff_test: {self.dir}README.md...")
            return True
        return False

    ###################################
    #
    # Helper methods
    #
    ###################################

    def log(self, verbose_message, short_message: Optional[str] = None):
        if self.verbose:
            print(verbose_message)
        elif short_message:
            print(short_message)

    def raise_or_print_fatal_errors(self, report: ErrorReport):
        """
        Errors that are thrown for the following reasons may be ignored
        if the --ignore_online_exceptions flag is passed. Otherwise,
        provide context for error.
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
                if not (self.dry_run or self.ignore_online_exceptions):
                    raise Exception(msg)
                print(f"Error checking {self.dir}: {msg}.")

    def get_dev_env_data(self, new_data: Dict) -> Dict:
        """
        URL checking on DEV will throw errors, so clean URLs:
        entity-api.dev -> entity.api
        """
        cleaned_data = defaultdict(dict)
        for key, value in new_data.get("validation", {}).items() or {}:
            if value is not None:
                new_url_data = [
                    dev_url_replace(v) for v in value.get("URL Errors", []) if value is not None
                ]
                if new_url_data:
                    value["URL Errors"] = new_url_data
            cleaned_data[key].update(value)
        new_data["validation"] = dict(cleaned_data)
        return new_data


def print_change_report(change_report: Dict, verbose: bool, globus_token: str):
    if change_report:
        print("-------CHANGE REPORT-------")
        if verbose:
            for dir, messages in change_report.items():
                print(f"{dir}: {', '.join([msg for msg in messages])}")
            print(
                f"""
                To update all, run:
                env PYTHONPATH=/ingest-validation-tools python -m tests-manual.update_test_data -t {' '.join([dir for dir in change_report.keys()])} --globus_token {globus_token} --verbose
                """
            )
        else:
            print("Dirs with errors:")
            for dir, _ in change_report.items():
                print(dir)


def manual_test(test_dir: Union[str, List], verbose: bool = False, full_diff: bool = False):
    """
    Mimics unittest behavior at the level of a single directory.
    """
    if type(test_dir) is str:
        assert Path(
            test_dir
        ).resolve(), f"Arg {test_dir} passed to manual_test is not a directory!"
    elif type(test_dir) is list and len(test_dir) > 1:
        test_dir = [dir for dir in test_dir if Path(dir).is_dir()]
    test = TestDatasetExamples()
    setattr(test, "dataset_test_dirs", test_dir)
    test.get_paths()
    test.test_validate_dataset_examples(verbose=verbose, full_diff=full_diff)


def get_opts(dir: str):
    if "dataset-examples" in dir:
        opts = DATASET_EXAMPLES_OPTS
    elif "dataset-iec-examples" in dir:
        opts = DATASET_IEC_EXAMPLES_OPTS
    elif "plugin-tests" in dir:
        opts = PLUGIN_EXAMPLES_OPTS
    else:
        opts = {}
    if args.env == "DEV":
        opts = opts | {
            "app_context": {
                "ingest_url": "https://ingest-api.dev.hubmapconsortium.org/",
                "entities_url": "https://entity-api.dev.hubmapconsortium.org/entities/",
                "request_header": {"X-Hubmap-Application": "ingest-pipeline"},
            }
        }
    return opts


def call_update(dir: str, args) -> Dict:
    change_report = UpdateData(
        dir,
        args.globus_token,
        opts=get_opts(dir),
        dry_run=args.dry_run,
        verbose=args.verbose,
        exclude=args.exclude,
        full_diff=args.full_diff,
        update_from_fixtures=args.update_from_fixtures,
        ignore_online_exceptions=args.ignore_online_exceptions,
        env=args.env,
    ).update_test_data()
    return change_report


parser = argparse.ArgumentParser(
    description="Update README.md and fixtures.json files for a given example directory by passing the directory name (the parent of the upload directory) and a Globus token."
)
parser.add_argument(
    "-t",
    "--target_dirs",
    help="""
    [Required] The directory or directories containing the target README.md and fixtures.json files to update. Can pass multiple directories, e.g. '-t examples/dataset-examples/a examples/dataset-examples/b'.
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
    help="[Optional for manual_test] Token obtained from Globus, e.g. can be found in the Authorization header when you are logged in to Ingest UI. Omit 'Bearer' portion.",
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
    help="[Optional] Specify if you want to skip writing either README or fixtures. Can only accept one argument; use --dry_run if you want to preview output.",
)
parser.add_argument(
    "-m",
    "--manual_test",
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
    "--update_from_fixtures",
    action="store_true",
    help="[Optional] Default is False. Update based on fixture data rather than making online calls. Use only when certain of fixture data!",
)

parser.add_argument(
    "--env",
    choices=["DEV", "PROD"],
    default=["PROD"],
    help="[Optional] Run tests against an env other than PROD by passing dev-specific app_context.",
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


def get_sub_dirs(target_dir: str) -> List[str]:
    if Path(target_dir).absolute() in [Path(path).absolute() for path in parent_dirs]:
        sub_dirs = [
            example_dir
            for example_dir in glob.glob(f"{target_dir}/**")
            if Path(example_dir).is_dir()
        ]
        return sorted(sub_dirs)
    return [target_dir]


def run_manual_test(target_dirs: List, args):
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
        manual_test([sub_dir], verbose=args.verbose, full_diff=args.full_diff)


def run_update(target_dirs: List, args):
    change_report = {}
    if target_dirs in [["examples/"], ["examples"]]:
        target_dirs = parent_dirs
    for dir in target_dirs:
        sub_dirs = get_sub_dirs(dir)
        for sub_dir in sub_dirs:
            change_report.update(call_update(str(sub_dir), args))
    return change_report


if args.manual_test:
    run_manual_test(args.target_dirs, args)
else:
    change_report = run_update(args.target_dirs, args)
    print_change_report(change_report, verbose=args.verbose, globus_token=args.globus_token)
