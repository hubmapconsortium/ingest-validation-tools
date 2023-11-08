#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path
import inspect
from datetime import datetime

from ingest_validation_tools.error_report import ErrorReport
from ingest_validation_tools.upload import Upload
from ingest_validation_tools.cli_utils import ShowUsageException, exit_codes, dir_path
from ingest_validation_tools.check_factory import cache_path

directory_schemas = sorted(
    {
        p.stem
        for p in (
            Path(__file__).parent / "ingest_validation_tools" / "directory-schemas"
        ).glob("*.yaml")
    }
)


def make_parser():
    parser = argparse.ArgumentParser(
        description="""
Validate a HuBMAP upload, both the metadata TSVs and the datasets.
If you only want to validate a TSV in isolation, look at validate_tsv.py.""",
        epilog=f"""
Typical usage:
  --local_directory: Used by lab before upload, and on Globus after upload.

  --local_directory + --dataset_ignore_globs + --upload_ignore_globs:
  After the initial validation on Globus, the metadata TSVs are broken up,
  and one-line TSVs are put in each dataset directory. This structure needs
  extra parameters.

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

    # Should validation be loosened?

    parser.add_argument(
        "--optional_fields",
        nargs="+",
        metavar="FIELD",
        default=[],
        help="The listed fields will be treated as optional. "
        "(But if they are supplied in the TSV, they will be validated.)",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Skip checks that require network access.",
    )
    parser.add_argument(
        "--clear_cache",
        action="store_true",
        help="Clear cache of network check responses.",
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

    # Are there plugin validations?

    parser.add_argument(
        "--plugin_directory", action="store", help="Directory of plugin tests."
    )
    parser.add_argument(
        "--run_plugins",
        required=False,
        action="store_true",
        help="Run plugin validation even if there are upstream errors.",
    )

    # Arguments for manual tests
    parser.add_argument(
        "--globus_token",
        help="Token for URL checking using Entity API.",
    )
    parser.add_argument(
        "--cedar_api_key",
        help="CEDAR Metadata Spreadsheet Validator API key.",
    )
    # How should output be formatted?

    error_report_methods = [
        name
        for (name, type) in inspect.getmembers(ErrorReport)
        if name.startswith("as_")
    ]
    parser.add_argument(
        "--output", choices=error_report_methods, default="as_text_list"
    )

    parser.add_argument(
        "--add_notes",
        action="store_true",
        help="Append a context note to error reports.",
    )
    parser.add_argument(
        "--save_report",
        action="store_true",
        help='Save the report; Adding "--upload_ignore_globs '
        "'report-*.txt'\" is necessary to revalidate.",
    )

    return parser


# We want the error handling inside the __name__ == '__main__' section
# to be able to show the usage string if it catches a ShowUsageException.
# Defining this at the top level makes that possible.
parser = make_parser()


def _save_report(upload, report):
    timestamp = datetime.today().strftime("%Y-%m-%d_%H-%M-%S")
    report_path = upload.directory_path / f"report-{timestamp}.txt"
    report_path.write_text(report.as_text_list())


def main():
    args = parser.parse_args()

    if args.clear_cache:
        cache_path.unlink()

    upload_args = {
        "add_notes": args.add_notes,
        "encoding": args.encoding,
        "offline": args.offline,
        "globus_token": args.globus_token,
        "cedar_api_key": args.cedar_api_key,
        "optional_fields": args.optional_fields,
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
    if args.cedar_api_key:
        upload_args["cedar_api_key"] = args.cedar_api_key

    upload = Upload(**upload_args)
    info = upload.get_info()
    errors = upload.get_errors()
    report = ErrorReport(info=info, errors=errors)
    print(getattr(report, args.output)())
    if args.save_report:
        _save_report(upload, report)
    return exit_codes.INVALID if errors else exit_codes.VALID


if __name__ == "__main__":
    try:
        exit_status = main()
    except ShowUsageException as e:
        print(parser.format_usage(), file=sys.stderr)
        print(e, file=sys.stderr)
        exit_status = exit_codes.ERROR
    sys.exit(exit_status)
