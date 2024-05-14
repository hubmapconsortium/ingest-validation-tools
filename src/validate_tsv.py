#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path

from yaml import dump

from ingest_validation_tools.cli_utils import ShowUsageException, exit_codes
from ingest_validation_tools.message_munger import recursive_munge
from ingest_validation_tools.schema_loader import PreflightError
from ingest_validation_tools.validation_utils import get_schema_version, get_tsv_errors

reminder = (
    "REMINDER: Use of validate_tsv.py is deprecated; use the HuBMAP Metadata Spreadsheet Validator"
    " to validate single TSVs instead (https://metadatavalidator.metadatacenter.org)."
)


def make_parser():
    parser = argparse.ArgumentParser(
        description=f"Validate a HuBMAP TSV. {reminder}",
        epilog=f"""
Exit status codes:
  {exit_codes.VALID}: Validation passed
  {exit_codes.BUG}: Unexpected bug
  {exit_codes.ERROR}: User error
  {exit_codes.INVALID}: Validation failed
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--path", required=True, help="TSV path")
    parser.add_argument(
        "--schema",
        required=True,
        choices=[
            "sample",
            "sample-block",
            "sample-suspension",
            "sample-section",
            "antibodies",
            "contributors",
            "metadata",
            "source",
        ],
    )
    parser.add_argument(
        "--globus_token",
        default="",
        required=False,
        help="Token for URL checking using Entity API.",
    )
    parser.add_argument("--output", choices=["as_text", "as_md"], default="as_text")
    return parser


# We want the error handling inside the __name__ == '__main__' section
# to be able to show the usage string if it catches a ShowUsageException.
# Defining this at the top level makes that possible.
parser = make_parser()


def as_text(errors) -> str:
    if errors:
        return dump(recursive_munge(errors), sort_keys=False)
    return "No errors!\n"


def as_md(errors) -> str:
    return f"```\n{as_text(errors)}```"


def main():
    args = parser.parse_args()
    try:
        schema_version = get_schema_version(Path(args.path), "ascii")
        schema_name = schema_version.schema_name
        errors_string = f"{schema_version.schema_name}-v{schema_version.version}"
    except PreflightError as e:
        errors = {"Preflight": str(e)}
    else:
        errors = get_tsv_errors(args.path, schema_name=schema_name, globus_token=args.globus_token)
        errors = {f"{errors_string} TSV errors": errors} if errors else {}
    print(eval(args.output)(errors))
    return exit_codes.INVALID if errors else exit_codes.VALID


if __name__ == "__main__":
    try:
        exit_status = main()
    except ShowUsageException as e:
        print(parser.format_usage(), file=sys.stderr)
        print(e, file=sys.stderr)
        exit_status = exit_codes.ERROR
    print(reminder)
    sys.exit(exit_status)
