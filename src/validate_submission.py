#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path
import inspect

from ingest_validation_tools.error_report import ErrorReport
from ingest_validation_tools.submission import Submission
from ingest_validation_tools import argparse_types
from ingest_validation_tools.argparse_types import ShowUsageException


directory_schemas = sorted({
    p.stem for p in
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
  --tsv_paths: Used to validate TSVs in isolation, without checking references.

  --local_directory: Used in development against test fixtures, and could be used
  by labs before submission.

  --local_directory + --dataset_ignore_globs + --submission_ignore_globs:
  Currently, during ingest, the metadata TSVs are broken up, and one-line TSVs
  are put in each dataset directory. This structure needs extra ignores.

''',
        formatter_class=argparse.RawDescriptionHelpFormatter)

    # What should be validated?

    mutex_group = parser.add_mutually_exclusive_group()
    mutex_group.add_argument(
        '--local_directory', type=argparse_types.dir_path,
        metavar='PATH',
        help='Local directory to validate')
    mutex_group.add_argument(
        '--tsv_paths', nargs='+',
        metavar='PATH',
        help='Paths of metadata.tsv files.')

    # Should validation be loosened?

    parser.add_argument(
        '--optional_fields', nargs='+',
        metavar='FIELD',
        help='The listed fields will be treated as optional. '
        '(But if they are supplied in the TSV, they will be validated.)'
    )
    parser.add_argument(
        '--offline', action='store_true',
        help='Skip checks that require network access.'
    )

    default_ignore = '.*'
    parser.add_argument(
        '--dataset_ignore_globs', nargs='+',
        metavar='GLOB',
        default=[default_ignore],
        help=f'Matching files in each dataset directory will be ignored. Default: {default_ignore}'
    )
    parser.add_argument(
        '--submission_ignore_globs', nargs='+',
        metavar='GLOB',
        help='Matching sub-directories in the submission will be ignored.'
    )

    default_encoding = 'ascii'
    parser.add_argument(
        '--encoding', default=default_encoding,
        help=f'Character-encoding to use for parsing TSVs. Default: {default_encoding}. '
        'Work-in-progress: https://github.com/hubmapconsortium/ingest-validation-tools/issues/494'
    )

    # Are there plugin validations?

    parser.add_argument('--plugin_directory', action='store',
                        help='Directory of plugin tests.')

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
    if not (args.tsv_paths or args.local_directory):
        raise ShowUsageException(
            'Either local file or local directory is required')

    return args


def main():
    args = parse_args()
    submission_args = {
        'add_notes': args.add_notes,
        'encoding': args.encoding,
        'offline': args.offline,
        'optional_fields': args.optional_fields or []
    }

    if args.local_directory:
        submission_args['directory_path'] = Path(args.local_directory)

    if args.tsv_paths:
        submission_args['tsv_paths'] = args.tsv_paths

    if args.dataset_ignore_globs:
        submission_args['dataset_ignore_globs'] = \
            args.dataset_ignore_globs
    if args.submission_ignore_globs:
        submission_args['submission_ignore_globs'] = \
            args.submission_ignore_globs
    if args.plugin_directory:
        submission_args['plugin_directory'] = \
            args.plugin_directory

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
