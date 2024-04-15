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
from ingest_validation_tools.schema_loader import SchemaVersion
from ingest_validation_tools.table_validator import ReportType
from ingest_validation_tools.upload import Upload
from ingest_validation_tools.validation_utils import TSVError, read_rows
from tests.test_dataset_examples import (
    DATASET_EXAMPLES_OPTS,
    DATASET_IEC_EXAMPLES_OPTS,
    MockException,
    TestDatasetExamples,
    clean_report,
    dataset_test,
    dev_url_replace,
    diff_test,
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
        env: str = "PROD",
    ):
        self.dir = dir
        self.globus_token = globus_token
        self.exclude = exclude
        self.opts = opts if opts else DATASET_EXAMPLES_OPTS
        self.verbose = verbose
        self.upload_verbose = True if "plugin-tests" in dir else False
        self.dry_run = dry_run
        self.full_diff = full_diff
        self.env = env

    def log(self, verbose_message, short_message: Optional[str] = None):
        if self.verbose:
            print(verbose_message)
        elif short_message:
            print(short_message)

    def update_test_data(self) -> Dict[str, List]:
        print(f"Evaluating {self.dir}...")
        self.change_report = defaultdict(list)
        self.upload = Upload(
            Path(f"{self.dir}/upload"),
            globus_token=self.globus_token,
            **self.opts,
            verbose=self.upload_verbose,
        )
        errors = self.upload.get_errors()
        info = self.upload.get_info()
        report = ErrorReport(info=info, errors=errors)
        if "Too Many Requests" in report.as_md():
            raise Exception(
                f"Something went wrong with Spreadsheet Validator request for {self.dir}."
            )
        # Necessary to avoid including 'Unauthorized' in output when no Globus token is provided,
        # but only relevant for entity-api links.
        elif (
            "No token" in report.as_md()
            or "Unauthorized for url: https://entity.api" in report.as_md()
        ):
            raise Exception(
                f"URL checking returned 'Unauthorized' in response while checking {self.dir}; did you forget a Globus token?"
            )
        if "fixtures" not in self.exclude:
            new_data = self.update_fixtures(report)
            if self.env == "DEV":
                for value in new_data.get("validation", {}).values() or {}:
                    if value is not None:
                        new_url_data = [
                            dev_url_replace(v)
                            for v in value.get("URL Errors", [])
                            if value is not None
                        ]
                        if new_url_data:
                            value["URL Errors"] = new_url_data
            fixtures = self.open_or_create_fixtures()
            diff = DeepDiff(
                fixtures,
                new_data,
                ignore_order=True,
                report_repetition=True,
            )
            if not diff:
                print(f"No diff found, skipping {self.dir}/fixtures.json...")
            elif self.dry_run:
                self.log(
                    f"""
                        Diff:
                        {diff}

                        Would have written the following to {self.dir}/fixtures.json:
                        {new_data}
                        """,
                    short_message=f"Would have updated {self.dir}/fixtures.json.",
                )
                self.change_report[self.dir].append("Fixtures diff found")
            else:
                print(f"Writing to {self.dir}/fixtures.json...")
                with open(f"{self.dir}/fixtures.json", "w") as f:
                    json.dump(new_data, f)
        else:
            print(f"{self.dir}/fixtures.json excluded, not changed.")
        cleaned_report = clean_report(report)
        if "README" not in self.exclude:
            readme = self.open_or_create_readme()
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
                print(f"No diff found, skipping {self.dir}/README.md")
            except MockException:
                return {}
            except AssertionError:
                print(f"FAILED diff_test: {self.dir}/README.md...")
                if self.dry_run:
                    self.log(
                        f"""
                            Would have written the following report to {self.dir}/README.md:
                            {cleaned_report}
                            """,
                        f"Would have updated {self.dir}/README.md.",
                    )
                    self.change_report[self.dir].append("README diff found")
                else:
                    self.log(
                        f"""
                            Writing the following report to {self.dir}/README.md:
                            {cleaned_report}
                            """,
                        f"Updating {self.dir}/README.md.",
                    )
                    with open(f"{self.dir}/README.md", "w") as f:
                        f.write(cleaned_report)
                    dataset_test(self.dir, self.opts | {"globus_token": self.globus_token})
        else:
            print(f"{self.dir}/README.md excluded, not changed.")
        return self.change_report

    def update_fixtures(self, report: ErrorReport) -> Dict:
        new_data = {}
        new_assaytype_data = {}
        new_validation_data = {}
        for path, schema in self.upload.effective_tsv_paths.items():
            new_assaytype_data[schema.dataset_type] = schema.soft_assay_data
            if "Preflight" in report.as_md():
                continue
            if schema.is_cedar:
                new_validation_data[schema.schema_name] = self.upload.online_checks(
                    path, schema, ReportType.STR
                )
            for other_type, paths in {
                "antibodies": schema.antibodies_paths,
                "contributors": schema.contributors_paths,
            }.items():
                for path in paths:
                    try:
                        validation = self.other_type_online_checks(path, other_type)
                    except TSVError:
                        continue
                    if validation:
                        new_validation_data.update(validation)
        new_data["assaytype"] = new_assaytype_data
        new_data["validation"] = new_validation_data
        return new_data

    def other_type_online_checks(self, path: str, other_type: str) -> Dict:
        metadata_schema_id = read_rows(Path(path), "ascii")[0].get("metadata_schema_id")
        if metadata_schema_id:
            return {
                Path(path).stem: self.upload.online_checks(
                    path, SchemaVersion(schema_name=other_type, is_cedar=True), ReportType.STR
                )
            }
        return {}

    def open_or_create_fixtures(self) -> Dict:
        if not Path(f"{self.dir}/fixtures.json").exists():
            open(f"{self.dir}/fixtures.json", "w")
        with open(f"{self.dir}/fixtures.json", "r") as f:
            try:
                fixtures = json.load(f)
            except JSONDecodeError:
                fixtures = {}
        return fixtures

    def open_or_create_readme(self):
        if not Path(f"{self.dir}/README.md").exists():
            open(f"{self.dir}/README.md", "w")
        return open(f"{self.dir}/README.md", "r")


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


def manual_test(test_dir: Union[str, List], verbose: bool = False):
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
    test.test_validate_dataset_examples(verbose=verbose)


def call_update(dir: str, args) -> Dict:
    if "dataset-examples" in dir:
        opts = DATASET_EXAMPLES_OPTS
    elif "dataset-iec-examples" in dir:
        opts = DATASET_IEC_EXAMPLES_OPTS
    elif "plugin-tests" in dir:
        opts = DATASET_IEC_EXAMPLES_OPTS | {
            "plugin_directory": Path(
                "../ingest-validation-tests/src/ingest_validation_tests"
            ).resolve()
        }
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
    change_report = UpdateData(
        dir,
        args.globus_token,
        opts=opts,
        dry_run=args.dry_run,
        verbose=args.verbose,
        exclude=args.exclude,
        full_diff=args.full_diff,
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
    The directory or directories containing the target README.md and fixtures.json files to update. Can pass multiple directories, e.g. '-t examples/dataset-examples/a examples/dataset-examples/b'.
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
    help="Token obtained from Globus, e.g. can be found in the Authorization header when you are logged in to Ingest UI. Omit 'Bearer' portion.",
    required=True,
    type=str,
)
parser.add_argument(
    "-d",
    "--dry_run",
    action="store_true",
    help="Default is False. If specified, do not write data but instead print output.",
)
parser.add_argument(
    "-v",
    "--verbose",
    action="store_true",
    help="Default is False. If specified, prints more verbose output.",
)
parser.add_argument(
    "-e",
    "--exclude",
    choices=["README", "fixtures"],
    default=[],
    help="Specify if you want to skip writing either README or fixtures. Can only accept one argument; use --dry_run if you want to preview output.",
)
parser.add_argument(
    "-m",
    "--manual_test",
    action="store_true",
    help="Default is False. Used for investigating testing failures with more verbose output. Requires passing a test_dir. Pass a blank Globus token as this runs offline.",
)
parser.add_argument(
    "-f",
    "--full_diff",
    action="store_true",
    help="Default is False. Show full and cleaned README diff.",
)
parser.add_argument(
    "--env",
    choices=["DEV", "PROD"],
    default=["PROD"],
    help="Run tests against an env other than PROD by passing dev-specific app_context.",
)

args = parser.parse_args()
# tsv-examples not currently integrated, could be if needed.
parent_dirs = [
    Path("examples/dataset-examples").absolute(),
    Path("examples/dataset-iec-examples").absolute(),
    Path("examples/plugin-tests").absolute(),
]
if args.manual_test:
    for dir in args.target_dirs:
        if Path(dir).absolute() in parent_dirs:
            sub_dirs = [example_dir for example_dir in glob.glob(f"{dir}/**")]
            for dir in sub_dirs:
                manual_test([dir], verbose=args.verbose)
        else:
            manual_test([dir], verbose=args.verbose)
else:
    change_report = {}
    if args.target_dirs in [["examples/"], ["examples"]]:
        args.target_dirs = [
            "examples/dataset-examples",
            "examples/dataset-iec-examples",
            "examples/plugin-tests",
        ]
    for dir in args.target_dirs:
        if Path(dir).absolute() in parent_dirs:
            dirs = [example_dir for example_dir in glob.glob(f"{dir}/**")]
            for dir in dirs:
                change_report.update(call_update(dir, args))
        else:
            change_report.update(call_update(dir, args))
    print_change_report(change_report, verbose=args.verbose, globus_token=args.globus_token)
