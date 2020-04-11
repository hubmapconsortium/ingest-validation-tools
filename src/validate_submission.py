#!/usr/bin/env python3

import argparse
import sys
import re
from pathlib import Path
from glob import glob
import csv

from ingest_validation_tools.error_report import ErrorReport
from ingest_validation_tools.submission import Submission
from ingest_validation_tools import argparse_types
from ingest_validation_tools.globus_utils import get_globus_connection_error


def parse_args():
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

    expected_type_metadata_form = \
        f'<{"|".join(argparse_types.directory_schemas)}>:<local_path_to_tsv>'
    parser.add_argument(
        '--type_metadata', type=argparse_types.type_metadata_pair, nargs='+',
        metavar='TYPE_PATH',
        help='A list of type / metadata.tsv pairs '
        f'of the form "{expected_type_metadata_form}".')

    args = parser.parse_args()
    if not any([
        args.local_directory,
        args.globus_url,
        args.globus_origin_directory,
        args.type_metadata
    ]):
        raise ShowUsageException(
            parser.format_usage() +
            'At least one argument is required')

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

    submission_args = {}
    if args.local_directory:
        submission_args['directory_path'] = Path(args.local_directory)
    if args.type_metadata:
        submission_args['override_tsv_paths'] = {
            pair['type']: pair['path'] for pair in args.type_metadata
        }
    submission = Submission(**submission_args)
    errors = submission.get_errors()
    report = ErrorReport(submission.get_errors())
    print(report.as_text())
    return 1 if errors else 0

class ShowUsageException(Exception):
    pass

#
# def _validate_metadata_tsv_messages(type, metadata_path):
#     try:
#         validate_metadata_tsv(type=type, metadata_path=metadata_path)
#         logging.info('PASS')
#         return []
#     except TableValidationErrors as e:
#         logging.warning('FAIL')
#         return [str(e)]
#
#
# def _validate_data_path_messages(type, data_path):
#     logging.info(f'Validating {type} {data_path}')
#     try:
#         validate_data_path(type=type, data_path=data_path)
#         logging.info('PASS')
#         return []
#     except DirectoryValidationErrors as e:
#         logging.warning('FAIL')
#         return [str(e)]
#
#
# def _validate_submission_directory_messages(submission_directory):
#     metadata_glob = submission_directory + '/*-metadata.tsv'
#     metadata_tsvs = glob(metadata_glob)
#     if not metadata_tsvs:
#         raise ShowUsageException(f'Nothing matched {metadata_glob}')
#     messages = []
#     for tsv_path in metadata_tsvs:
#         dir_type = re.match(r'(.+)-metadata\.tsv$', Path(tsv_path).name)[1]
#         table_type = dir_type.split('-')[0]
#         messages += _validate_metadata_tsv_messages(table_type, tsv_path)
#
#         with open(tsv_path) as f:
#             rows = list(csv.DictReader(f, dialect='excel-tab'))
#             if not rows:
#                 raise ShowUsageException(f'{tsv_path} is empty')
#             for row in rows:
#                 full_data_path = Path(submission_directory) / row['data_path']
#                 messages += _validate_data_path_messages(
#                     dir_type, full_data_path)
#
#     return messages
#
#
# class ShowUsageException(Exception):
#     # Throw this when there it a problem with the validation process
#     # (not just that validation failed) an you don't want a stack trace.
#     pass
#
#
# def _print_message(
#         dir, type,
#         periods=False, skip_data_path=False):
#     # Doctests choke on blank lines: periods=True replaces with "." for now.
#     try:
#         validate(dir, type, skip_data_path=skip_data_path)
#         logging.info('PASS')
#         return 0
#     except DirectoryValidationErrors as e:
#         message = str(e)
#         if periods:
#             message = re.sub(r'\n(\s*\n)+', '\n.\n', message).strip()
#         # End user just wants a name, and doesn't care about refs.
#         message = re.sub(r"\$ref: '#/definitions/(\w+)'", r'\1', message)
#         # Ad hoc rewrites: Perhaps move these up to the library?
#         message = message.replace(
#             'fails this "oneOf" check',
#             'should be one of these')
#         message = message.replace(
#             'fails this "contains" check',
#             'should contain')
#
#         print(message)
#         logging.warning('FAIL')
#         return 1
#     except TableValidationErrors as e:
#         message = str(e)
#         if periods:
#             message = re.sub(r'\n(\s*\n)+', '\n.\n', message).strip()
#         print(message)
#         logging.warning('FAIL')
#         return 2


if __name__ == "__main__":
    try:
        exit_status = main()
    except ShowUsageException as e:
        print(e, file=sys.stderr)
        exit_status = 2
    sys.exit(exit_status)
