import argparse
import glob
import json
from collections import defaultdict
from json.decoder import JSONDecodeError
from pathlib import Path
from typing import Dict, List, Optional, Union

from ingest_validation_tools.cli_utils import dir_path
from ingest_validation_tools.error_report import ErrorReport
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
    ):
        self.dir = dir
        self.globus_token = globus_token
        self.exclude = exclude
        self.opts = opts if opts else DATASET_EXAMPLES_OPTS
        self.verbose = verbose
        self.upload_verbose = True if "plugin-tests" in dir else False
        self.dry_run = dry_run

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
        info = self.upload.get_info()
        errors = self.upload.get_errors()
        report = ErrorReport(info=info, errors=errors)
        if "Too many requests" in report.as_md():
            raise Exception(
                f"Something went wrong with Spreadsheet Validator request for {self.dir}."
            )
        if "fixtures" not in self.exclude:
            new_data = self.update_fixtures(report)
            fixtures = self.open_or_create_fixtures()
            if fixtures == new_data:
                print(f"No diff found, skipping {self.dir}/fixtures.json...")
            elif self.dry_run:
                self.log(
                    f"""
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
        if "README" not in self.exclude:
            readme = self.open_or_create_readme()
            try:
                diff_test(self.dir, readme, clean_report(report), verbose=self.verbose)
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
                            {clean_report(report)}
                            """,
                        f"Would have updated {self.dir}/README.md.",
                    )
                    self.change_report[self.dir].append("README diff found")
                else:
                    self.log(
                        f"""
                            Writing the following report to {self.dir}/README.md:
                            {clean_report(report)}
                            """,
                        f"Updating {self.dir}/README.md.",
                    )
                    with open(f"{self.dir}/README.md", "w") as f:
                        # TODO: issues with blank lines at end of report
                        f.write(clean_report(report))
                    dataset_test(self.dir, self.opts)
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
                    path, schema.schema_name, ReportType.STR
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
            return {Path(path).stem: self.upload.online_checks(path, other_type, ReportType.STR)}
        return {}

    def open_or_create_fixtures(self):
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


def print_change_report(change_report: Dict):
    if change_report:
        print("-------CHANGE REPORT-------")
        for dir, messages in change_report.items():
            print(f"{dir}: {', '.join([msg for msg in messages])}")


def manual_test(test_dir: Union[str, List], verbose: bool = False):
    """
    Mimics unittest behavior at the level of a single directory.
    """
    if type(test_dir) is str:
        assert Path(
            test_dir
        ).resolve(), f"Arg {test_dir} passed to manual_test is not a directory!"
    elif type(test_dir) is list:
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
    change_report = UpdateData(
        dir,
        args.globus_token,
        opts=opts,
        dry_run=args.dry_run,
        verbose=args.verbose,
        exclude=args.exclude,
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

args = parser.parse_args()
# TODO: tsv-examples not currently integrated, could be if needed.
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
    print_change_report(change_report)
