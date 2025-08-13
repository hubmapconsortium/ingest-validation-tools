#!/usr/bin/env python3

import argparse
import inspect
import sys
from pathlib import Path

from ingest_validation_tools.cli_utils import ShowUsageException, dir_path, exit_codes
from ingest_validation_tools.error_report import ErrorReport
from ingest_validation_tools.upload import Upload

directory_schemas = sorted(
    {
        p.stem
        for p in (Path(__file__).parent / "ingest_validation_tools" / "directory-schemas").glob(
            "*.yaml"
        )
    }
)


def make_parser():
    parser = argparse.ArgumentParser(
        description="Validate a HuBMAP upload, both the metadata TSVs and the datasets.",
        epilog=f"""

Exit status codes:
  {exit_codes.VALID}: Validation passed
  {exit_codes.BUG}: Unexpected bug
  {exit_codes.ERROR}: User error
  {exit_codes.INVALID}: Validation failed
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # What should be validated?

    parser.add_argument(
        "--local_directory",
        type=dir_path,
        metavar="PATH",
        required=True,
        help="Local directory to validate",
    )

    parser.add_argument(
        "--offline_only",
        action="store_true",
        help="Skip URL checks (Spreadsheet Validator API checks still run).",
    )
    parser.add_argument(
        "--ignore_deprecation",
        action="store_true",
        help="Allow validation against deprecated versions of metadata schemas.",
    )

    default_ignore = ".*"
    parser.add_argument(
        "--dataset_ignore_globs",
        nargs="+",
        metavar="GLOB",
        default=[default_ignore],
        help=f"Matching files in each dataset directory will be ignored. Default: {default_ignore}",
    )
    parser.add_argument(
        "--upload_ignore_globs",
        nargs="+",
        metavar="GLOB",
        help="Matching files and subdirectories in the upload will be ignored.",
    )

    default_encoding = "ascii"
    parser.add_argument(
        "--encoding",
        default=default_encoding,
        help=f"Character-encoding to use for parsing TSVs. Default: {default_encoding}. "
        "Work-in-progress: https://github.com/hubmapconsortium/ingest-validation-tools/issues/494",
    )

    parser.add_argument("--plugin_directory", action="store", help="Directory of plugin tests.")
    parser.add_argument(
        "--run_plugins",
        required=False,
        action="store_true",
        help="Run plugin validation even if there are upstream errors.",
    )

    # Arguments for manual tests
    parser.add_argument(
        "--globus_token",
        default="",
        help="Token for URL checking using Entity API.",
    )
    error_report_methods = [
        name for (name, _) in inspect.getmembers(ErrorReport) if name.startswith("as_")
    ]
    parser.add_argument("--output", choices=error_report_methods, default="as_text_list")

    return parser


# We want the error handling inside the __name__ == '__main__' section
# to be able to show the usage string if it catches a ShowUsageException.
# Defining this at the top level makes that possible.
parser = make_parser()


def main():
    args = parser.parse_args()

    upload_args = {
        "encoding": args.encoding,
        "offline_only": args.offline_only,
        "globus_token": args.globus_token,
        "ignore_deprecation": args.ignore_deprecation,
        "run_plugins": args.run_plugins,
    }

    if args.local_directory:
        upload_args["directory_path"] = Path(args.local_directory)
    if args.dataset_ignore_globs:
        upload_args["dataset_ignore_globs"] = args.dataset_ignore_globs
    if args.upload_ignore_globs:
        upload_args["upload_ignore_globs"] = args.upload_ignore_globs
    if args.plugin_directory:
        upload_args["plugin_directory"] = args.plugin_directory
    if args.run_plugins:
        upload_args["run_plugins"] = args.run_plugins
    if args.globus_token:
        upload_args["globus_token"] = args.globus_token

    upload = Upload(**upload_args)
    report = ErrorReport(upload)
    print(getattr(report, args.output)())
    return exit_codes.INVALID if report.errors else exit_codes.VALID


if __name__ == "__main__":
    try:
        exit_status = main()
    except ShowUsageException as e:
        print(parser.format_usage(), file=sys.stderr)
        print(e, file=sys.stderr)
        exit_status = exit_codes.ERROR
    sys.exit(exit_status)
