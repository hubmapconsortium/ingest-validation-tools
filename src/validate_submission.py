#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path
import inspect

from ingest_validation_tools.error_report import ErrorReport
from ingest_validation_tools.submission import Submission
from ingest_validation_tools import argparse_types
from ingest_validation_tools.argparse_types import ShowUsageException
from ingest_validation_tools.globus_utils import get_globus_connection_error


def make_parser():
    parser = argparse.ArgumentParser(
        description='''
Validate a HuBMAP submission, both the metadata TSVs, and the datasets,
either local or remote, or a combination of the two.''',
        epilog='''
Typical usecases:

  --type_metadata + --globus_url: Validate one or more
  local metadata.tsv files against a submission directory already on Globus.

  --globus_url: Validate a submission directory on Globus,
  with <type>-metadata.tsv files in place.

  --local_directory: Used in development against test fixtures, and in
  the ingest-pipeline, where Globus is the local filesystem.
''',
        formatter_class=argparse.RawDescriptionHelpFormatter)

    # Is there a submission directory to validate?

    mutex_group = parser.add_mutually_exclusive_group()
    mutex_group.add_argument(
        '--local_directory', type=argparse_types.dir_path,
        metavar='PATH',
        help='Local directory to validate')
    mutex_group.add_argument(
        '--globus_url', type=argparse_types.globus_url,
        metavar='URL',
        help='The Globus File Manager URL of a directory to validate. '
        'TODO: Not yet implemented.')
    mutex_group.add_argument(
        '--globus_origin_directory', type=argparse_types.origin_directory_pair,
        metavar='ORIGIN_PATH',
        help='A Globus submission directory to validate; '
        'Should have the form "<globus_origin_id>:<globus_path>". '
        'TODO: Not yet implemented.')

    # Is there metadata to validate?

    expected_type_metadata_form = \
        f'<{"|".join(argparse_types.directory_schemas)}>:<local_path_to_tsv>'
    parser.add_argument(
        '--type_metadata', type=argparse_types.type_metadata_pair, nargs='+',
        metavar='TYPE_PATH',
        help='A list of type / metadata.tsv pairs '
        f'of the form "{expected_type_metadata_form}".')

    # How should output be formatted?

    error_report_methods = [
        name for (name, type) in inspect.getmembers(ErrorReport)
        if name.startswith('as_')
    ]
    parser.add_argument('--output', choices=error_report_methods,
                        default='as_text')

    parser.add_argument('--add_notes', action='store_true',
                        help='Append a context note to error reports.')

    return parser


# We want the error handling inside the __name__ == '__main__' section
# to be able to show the usage string if it catches a ShowUsageException.
# Defining this at the top level makes that possible.
parser = make_parser()


def parse_args():
    args = parser.parse_args()
    if not any([
        args.local_directory,
        args.globus_url,
        args.globus_origin_directory,
        args.type_metadata
    ]):
        raise ShowUsageException('At least one argument is required')

    return args


def main():
    args = parse_args()

    globus = args.globus_url or args.globus_origin_directory
    if globus:
        error_message = get_globus_connection_error(globus['origin'])
        if error_message:
            raise ShowUsageException(error_message)

        raise ShowUsageException('TODO: Globus not yet supported')
        # TODO: mirror directory to local cache.

    submission_args = {'add_notes': args.add_notes}
    if args.local_directory:
        submission_args['directory_path'] = Path(args.local_directory)
    if args.type_metadata:
        submission_args['override_tsv_paths'] = {
            pair['type']: pair['path'] for pair in args.type_metadata
        }
    submission = Submission(**submission_args)
    errors = submission.get_errors()
    report = ErrorReport(errors)
    print(getattr(report, args.output)())
    return 1 if errors else 0


if __name__ == "__main__":
    try:
        exit_status = main()
    except ShowUsageException as e:
        print(parser.format_usage(), file=sys.stderr)
        print(e, file=sys.stderr)
        exit_status = 2
    sys.exit(exit_status)
