#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path
import inspect

from ingest_validation_tools.error_report import ErrorReport
from ingest_validation_tools.submission import Submission
from ingest_validation_tools import argparse_types
from ingest_validation_tools.argparse_types import ShowUsageException
from ingest_validation_tools.globus_utils import (
    get_globus_connection_error, get_globus_cache_path)


directory_schemas = sorted({
    p.stem.split('-')[0] for p in
    (Path(__file__).parent / 'ingest_validation_tools' /
     'directory-schemas').glob('*.yaml')
})


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
        help='The Globus File Manager URL of a directory to validate.')
    mutex_group.add_argument(
        '--globus_origin_directory', type=argparse_types.origin_directory_pair,
        metavar='ORIGIN_PATH',
        help='A Globus submission directory to validate; '
        'Should have the form "<globus_origin_id>:<globus_path>".')

    # Is there metadata to validate?

    parser.add_argument(
        '--type_metadata', nargs='+',
        metavar='TYPE PATH',
        help='A list of type / metadata.tsv pairs. '
        f'Type should be one of: {directory_schemas}')

    parser.add_argument(
        '--optional_fields', nargs='+',
        metavar='FIELD',
        help='The listed fields will be treated as optional. '
        '(But if they are supplied in the TSV, they will be validated.)'
    )

    parser.add_argument(
        '--dataset_ignore_globs', nargs='+',
        metavar='GLOB',
        default=['.*'],
        help='Matching files in each dataset directory will be ignored.'
    )
    parser.add_argument(
        '--submission_ignore_globs', nargs='+',
        metavar='GLOB',
        help='Matching sub-directories in the submission will be ignored.'
    )

    # How should output be formatted?

    error_report_methods = [
        name for (name, type) in inspect.getmembers(ErrorReport)
        if name.startswith('as_')
    ]
    parser.add_argument('--output', choices=error_report_methods,
                        default='as_text')

    parser.add_argument('--add_notes', action='store_true',
                        help='Append a context note to error reports.')

    # Permit the user to set the location of the plugin directory
    parser.add_argument('--plugin_dir_abs_path', action='store',
                        help='Absolute path of a directory of plugin tests.')

    return parser


# We want the error handling inside the __name__ == '__main__' section
# to be able to show the usage string if it catches a ShowUsageException.
# Defining this at the top level makes that possible.
parser = make_parser()


def parse_args():
    args = parser.parse_args()
    if not any([
        args.type_metadata,
        args.local_directory,
        args.globus_url,
        args.globus_origin_directory
    ]):
        raise ShowUsageException(
            'Either local file, local directory, or Globus is required')

    return args


def main():
    args = parse_args()
    submission_args = {
        'add_notes': args.add_notes,
        'optional_fields': args.optional_fields or []
    }

    globus = args.globus_url or args.globus_origin_directory
    if globus:
        error_message = get_globus_connection_error(globus['origin'])
        if error_message:
            raise ShowUsageException(error_message)
        submission_args['directory_path'] = get_globus_cache_path(
            globus['origin'], globus['path'])
    elif args.local_directory:
        submission_args['directory_path'] = Path(args.local_directory)

    if args.type_metadata:
        if 0 != len(args.type_metadata) % 2:
            raise ShowUsageException(
                'type_metadata should be a list with an even length')
        submission_args['override_tsv_paths'] = {}
        for i in range(len(args.type_metadata) // 2):
            type = args.type_metadata[2 * i]
            path = args.type_metadata[2 * i + 1]
            if type not in directory_schemas:
                raise ShowUsageException(
                    f'Expected one of {directory_schemas}, not "{type}"')
            if not Path(path).is_file():
                raise ShowUsageException(f'"{path}" is not a file')
            submission_args['override_tsv_paths'][type] = path

    if args.dataset_ignore_globs:
        submission_args['dataset_ignore_globs'] = \
            args.dataset_ignore_globs
    if args.submission_ignore_globs:
        submission_args['submission_ignore_globs'] = \
            args.submission_ignore_globs

    if args.plugin_dir_abs_path:
        submission_args['plugin_dir_abs_path'] = \
            args.plugin_dir_abs_path

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
