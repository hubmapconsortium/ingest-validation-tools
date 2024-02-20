import argparse
import glob
import json
from pathlib import Path
from typing import Dict, List

from ingest_validation_tools.cli_utils import dir_path
from ingest_validation_tools.error_report import ErrorReport
from ingest_validation_tools.table_validator import ReportType
from ingest_validation_tools.upload import Upload
from ingest_validation_tools.validation_utils import (
    get_schema_version,
    get_tsv_errors,
    read_rows,
)


def update_test_data(
    dir: str,
    globus_token: str,
    exclude: List = [],
    opts: Dict = {},
    dry_run: bool = False,
):
    if not opts:
        opts = {
            "dataset_ignore_globs": ["ignore-*.tsv", ".*"],
            "upload_ignore_globs": ["drv_ignore_*", "README_ONLINE"],
            "encoding": "ascii",
            "run_plugins": True,
        }
        upload = Upload(Path(f"{dir}/upload"), globus_token=globus_token, **opts)
        info = upload.get_info()
        errors = upload.get_errors()
        report = ErrorReport(info=info, errors=errors)
        if "README" not in exclude:
            with open(f"{dir}/README.md", "w") as f:
                if dry_run:
                    print(
                        f"""
                        Would have written the following report to {Path(f'{dir}/README.md')}:
                        {report.as_md()}
                        """
                    )
                else:
                    print(f"Writing to {Path(f'{dir}/README.md')}...")
                    f.write(report.as_md())
        else:
            print(f"{Path(f'{dir}/README.md')} excluded, not changed.")

        if "fixtures" not in exclude:
            new_data = {}
            with open(f"{dir}/fixtures.json", "w") as f:
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
                    if any(
                        substring in Path(file).name
                        for substring in ["contributors", "antibodies"]
                    )
                ]
                for file in other_files:
                    other_type = (
                        "contributors"
                        if "contributors" in file
                        else "antibodies" if "antibodies" in file else None
                    )
                    if other_type is None:
                        continue
                    is_cedar = bool(read_rows(Path(file), "ascii")[0].get("metadata_schema_id"))
                    if is_cedar:
                        new_validation_data[Path(file).stem] = upload.online_checks(
                            file, other_type, ReportType.JSON
                        )
                new_data["assaytype"] = new_assaytype_data
                new_data["validation"] = new_validation_data
                if dry_run:
                    print(
                        f"""
                        Would have written the following to {Path(f'{dir}/fixtures.json')}:
                        {new_data}
                        """
                    )
                else:
                    print(f"Writing to {Path(f'{dir}/fixtures.json')}...")
                    json.dump(new_data, f)
        else:
            print(f"{Path(f'{dir}/fixtures.md')} excluded, not changed.")
        # check_updated(dir)


# def check_updated(dir: str):
#


def update_tsv_readme(
    dir: str,
    schema: str,
    globus_token: str,
    exclude: List = [],
    opts: Dict = {},
    dry_run: bool = False,
):
    tsv_path = Path(f"{dir}/upload/{schema}.tsv")
    if not tsv_path.exists():
        print(f"No TSVs found in {tsv_path}, is this an intentionally failing example?")
        return
    if not opts.get("ingest_url"):
        opts["ingest_url"] = "https://ingest.api.hubmapconsortium.org/"
    schema_version = get_schema_version(tsv_path, "utf-8", opts.get("ingest_url", ""))
    schema_name = schema_version.schema_name
    errors = get_tsv_errors(dir, schema_name=schema_name, globus_token=globus_token)
    errors_string = f"{schema_version.schema_name}-v{schema_version.version}"
    errors = {f"{errors_string} TSV errors": errors} if errors else {}
    report = ErrorReport(info={}, errors=errors)
    if "README" not in exclude:
        if dry_run:
            print(
                f"""
                Would have written the following report to {Path(f'{dir}/README.md')}:
                {report.as_md()}
                """
            )
        else:
            with open(f"{dir}/README.md", "w") as f:
                print(f"Writing to {Path(f'{dir}/README.md')}...")
                f.write(report.as_md())
    else:
        print(f"{Path(f'{dir}/README.md')} excluded, not changed.")

    if "fixtures" not in exclude:
        if dry_run:
            print(
                f"""
                Would have written the following to {Path(f'{dir}/fixtures.json')}:
                {schema_version.soft_assay_data}
                """
            )
        else:
            with open(f"{dir}/fixtures.json", "w") as f:
                print(f"Writing to {Path(f'{dir}/fixtures.json')}...")
                json.dump(schema_version.soft_assay_data, f)
    else:
        print(f"{Path(f'{dir}/fixtures.md')} excluded, not changed.")


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
    Can also specify the following example directories to update all examples in each: 'examples/dataset-examples', 'examples/dataset-iec-examples', 'examples/tsv-examples'. Pass all with:
    -t examples/dataset-examples examples/dataset-iec-examples examples/tsv-examples'
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
    help="Default is False. If specified, do not write data but instead print output.",
    action="store_true",
)
parser.add_argument(
    "-e",
    "--exclude",
    choices=["README", "fixtures"],
    default=[],
    help="Specify if you want to skip writing either README or fixtures. Can only accept one argument; use --dry_run if you want to preview output.",
)
args = parser.parse_args()
parent_dirs = [
    Path("examples/dataset-examples").absolute(),
    Path("examples/dataset-iec-examples").absolute(),
]
for dir in args.target_dirs:
    if Path(dir).absolute() in parent_dirs:
        dirs = [example_dir for example_dir in glob.glob(f"{dir}/**")]
        for dir in dirs:
            update_test_data(
                dir, args.globus_token, opts=args.opts, dry_run=args.dry_run, exclude=args.exclude
            )

    elif Path(dir).absolute() == Path("examples/tsv-examples").absolute():
        tsv_example_dirs = [tsv_dir for tsv_dir in glob.glob(f"{dir}/**")]
        for tsv_sub_dir in tsv_example_dirs:
            schema = Path(tsv_sub_dir).name
            sub_dirs = [
                sub_dir for sub_dir in glob.glob(f"{tsv_sub_dir}/**") if Path(sub_dir).is_dir()
            ]
            for sub_dir in sub_dirs:
                update_tsv_readme(
                    sub_dir,
                    schema,
                    args.globus_token,
                    exclude=args.exclude,
                    opts=args.opts,
                    dry_run=args.dry_run,
                )
    update_test_data(
        dir, args.globus_token, opts=args.opts, dry_run=args.dry_run, exclude=args.exclude
    )
