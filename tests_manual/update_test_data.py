import argparse
import glob
import json
from json.decoder import JSONDecodeError
from pathlib import Path
from typing import Dict, List

from ingest_validation_tools.cli_utils import dir_path
from ingest_validation_tools.error_report import ErrorReport
from ingest_validation_tools.table_validator import ReportType
from ingest_validation_tools.upload import Upload
from ingest_validation_tools.validation_utils import TSVError, read_rows
from tests.test_dataset_examples import (
    DATASET_EXAMPLES_OPTS,
    DATASET_IEC_EXAMPLES_OPTS,
    TestDatasetExamples,
    clean_report,
    dataset_test,
    diff_test,
)


def update_test_data(
    dir: str,
    globus_token: str,
    exclude: List = [],
    opts: Dict = {},
    dry_run: bool = False,
    verbose: bool = False,
):
    if not opts:
        opts = {
            "dataset_ignore_globs": ["ignore-*.tsv", ".*"],
            "upload_ignore_globs": ["drv_ignore_*"],
            "encoding": "ascii",
            "run_plugins": True,
        }
    upload = Upload(Path(f"{dir}/upload"), globus_token=globus_token, **opts)
    info = upload.get_info()
    errors = upload.get_errors()
    report = ErrorReport(info=info, errors=errors)
    if "fixtures" not in exclude:
        new_data = {}
        new_assaytype_data = {}
        new_validation_data = {}
        for path, schema in upload.effective_tsv_paths.items():
            new_assaytype_data[schema.dataset_type] = schema.soft_assay_data
            for path, schema in upload.effective_tsv_paths.items():
                if schema.is_cedar:
                    new_validation_data[schema.dataset_type] = upload.online_checks(
                        path, schema.schema_name, ReportType.JSON
                    )
        other_files = [
            file
            for file in glob.glob(f"{dir}/upload/**")
            if any(substring in Path(file).name for substring in ["contributors", "antibodies"])
        ]
        for file in other_files:
            other_type = (
                "contributors"
                if "contributors" in file
                else "antibodies" if "antibodies" in file else None
            )
            if other_type is None:
                continue
            try:
                is_cedar = bool(read_rows(Path(file), "ascii")[0].get("metadata_schema_id"))
            except TSVError:
                continue
            if is_cedar:
                new_validation_data[Path(file).stem] = upload.online_checks(
                    file, other_type, ReportType.STR
                )
        new_data["assaytype"] = new_assaytype_data
        new_data["validation"] = new_validation_data
        if not Path(f"{dir}/fixtures.json").exists():
            open(f"{dir}/fixtures.json", "w")
        with open(f"{dir}/fixtures.json", "r") as f:
            try:
                fixtures = json.load(f)
            except JSONDecodeError:
                fixtures = {}
            if fixtures == new_data:
                print(f"No diff found, skipping {dir}/fixtures.json...")
            elif dry_run:
                if verbose:
                    print(
                        f"""
                        Would have written the following to {dir}/fixtures.json:
                        {new_data}
                        """
                    )
                else:
                    print(f"Would have updated {dir}/fixtures.json.")
            else:
                print(f"Writing to {dir}/fixtures.json...")
                with open(f"{dir}/fixtures.json", "w") as f:
                    json.dump(new_data, f)
    else:
        print(f"{dir}/fixtures.json excluded, not changed.")
    if "README" not in exclude:
        with open(f"{dir}/README.md", "r") as f:
            try:
                diff_test(dir, f, report.as_md(), verbose=verbose)
                print(f"No diff found, skipping {dir}/README.md")
            except AssertionError:
                print(f"FAILED diff_test: {dir}/README.md...")
                if dry_run:
                    if verbose:
                        print(
                            f"""
                            Would have written the following report to {dir}/README.md:
                            {clean_report(report)}
                            """
                        )
                    else:
                        print(f"Would have updated {dir}/README.md.")
                if not dry_run:
                    if verbose:
                        print(
                            f"""
                            Writing the following report to {dir}/README.md:
                            {clean_report(report)}
                            """
                        )
                    else:
                        print(f"Updating {dir}/README.md.")
                    with open(f"{dir}/README.md", "w") as f:
                        f.write(clean_report(report))
                    dataset_test(dir, opts)
    else:
        print(f"{dir}/README.md excluded, not changed.")


def single_test(test_dir: str):
    test = TestDatasetExamples()
    setattr(test, "dataset_test_dirs", test_dir)
    test.get_paths()
    test.test_validate_dataset_examples(verbose=True)


class StoreDictKeyPair(argparse.Action):
    # Solution updated from https://stackoverflow.com/a/42355279
    def __call__(self, parser, namespace, values, option_string=None):
        del parser, option_string
        opts = {}
        if not values or type(values) is not str:
            return
        for kv in values.split(","):
            k, v = kv.split("=")
            opts[k] = v
        setattr(namespace, self.dest, opts)


parser = argparse.ArgumentParser(
    description="Update README.md and fixtures.json files for a given example directory by passing the directory name (the parent of the upload directory) and a Globus token."
)
parser.add_argument(
    "-t",
    "--target_dirs",
    help="""
    The directory or directories containing the target README.md and fixtures.json files to update. Can pass multiple directories, e.g. '-t examples/dataset-examples/a examples/dataset-examples/b'.
    Can also specify the following example directories to update all examples in each: 'examples/dataset-examples', 'examples/dataset-iec-examples'. Pass all with:
    -t examples/dataset-examples examples/dataset-iec-examples
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
    "-o",
    "--opts",
    action=StoreDictKeyPair,
    default={},
    dest="opts",
    help="Additional optional arguments to pass to upload. Must be formatted 'key1=value1,key2=val2'. Opts will be applied to all target_dirs.",
    metavar="KEY1=VAL1,KEY2=VAL2",
    required=False,
)
parser.add_argument(
    "--dry_run",
    action="store_true",
    help="Default is False. If specified, do not write data but instead print output.",
)
parser.add_argument(
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
    "-s",
    "--single_test",
    action="store_true",
    help="Default is False. Used for investigating testing failures with more verbose output. Requires passing a test_dir. You can pass a blank Glubus ",
)
args = parser.parse_args()
parent_dirs = [
    Path("examples/dataset-examples").absolute(),
    Path("examples/dataset-iec-examples").absolute(),
]
if args.single_test:
    single_test(args.target_dirs)
else:
    if args.opts:
        opts = args.opts
    else:
        opts = {}
    for dir in args.target_dirs:
        if Path(dir).absolute() in parent_dirs:
            dirs = [example_dir for example_dir in glob.glob(f"{dir}/**")]
            for dir in dirs:
                if "dataset-examples" in dir:
                    opts = DATASET_EXAMPLES_OPTS
                elif "dataset-iec-examples" in dir:
                    opts = DATASET_IEC_EXAMPLES_OPTS
                update_test_data(
                    dir,
                    args.globus_token,
                    opts=opts,
                    dry_run=args.dry_run,
                    verbose=args.verbose,
                    exclude=args.exclude,
                )
        else:
            if "dataset-examples" in dir:
                opts = DATASET_EXAMPLES_OPTS
            elif "dataset-iec-examples" in dir:
                opts = DATASET_IEC_EXAMPLES_OPTS
            update_test_data(
                dir,
                args.globus_token,
                opts=opts,
                dry_run=args.dry_run,
                verbose=args.verbose,
                exclude=args.exclude,
            )
