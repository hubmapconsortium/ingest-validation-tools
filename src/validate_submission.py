#!/usr/bin/env python3

import argparse
import sys
import os
import re
import logging
from pathlib import Path
import subprocess
from glob import glob
import csv
import urllib

from directory_schema.errors import DirectoryValidationErrors

from ingest_validation_tools.validator import (
    validate, validate_metadata_tsv, validate_data_path, TableValidationErrors
)


def _dir_path(s):
    if os.path.isdir(s):
        return s
    else:
        raise Exception(f'"{s}" is not a directory')


def _origin_directory_pair(s):
    try:
        origin, path = s.split(':')
    except ValueError:
        raise argparse.ArgumentTypeError(
            f'Expected colon-delimited pair, not "{s}"')

    expected_format = r'[0-9a-f-]{36}'
    if not re.match(expected_format, origin):
        raise argparse.ArgumentTypeError(
            f'Origin format wrong; expected {expected_format}')

    return {
        'origin': origin,
        'path': path
    }


def _globus_url(s):
    '''
    >>> _globus_url('http://example.com/')
    Traceback (most recent call last):
    ...
    argparse.ArgumentTypeError: Expected a URL starting with https://app.globus.org/file-manager?

    >>> _globus_url('https://app.globus.org/file-manager?a=1')
    Traceback (most recent call last):
    ...
    argparse.ArgumentTypeError: Expected query keys to be ['origin_id', 'origin_path'], not ['a']

    >>> _globus_url('https://app.globus.org/file-manager?origin_id=32-hex-digits&origin_path=%2Fpath%2F')
    {'origin': '32-hex-digits', 'path': '/path/'}

    '''  # noqa E501
    expected_base = 'https://app.globus.org/file-manager?'
    if not s.startswith(expected_base):
        raise argparse.ArgumentTypeError(
            f'Expected a URL starting with {expected_base}')

    parsed = urllib.parse.urlparse(s)
    query = urllib.parse.parse_qs(parsed.query)
    expected_keys = ['origin_id', 'origin_path']
    actual_keys = sorted(query.keys())
    if actual_keys != expected_keys:
        raise argparse.ArgumentTypeError(
            f'Expected query keys to be {expected_keys}, not {actual_keys}')

    return {
        'origin': query['origin_id'][0],
        'path': query['origin_path'][0]
    }


def _type_metadata_pair(s):
    try:
        type, path = s.split(':')
    except ValueError:
        raise argparse.ArgumentTypeError(
            f'Expected colon-delimited pair, not "{s}"')

    if type not in _valid_types:
        raise argparse.ArgumentTypeError(
            f'Expected one of {_valid_types}, not "{type}"')

    if not Path(path).is_file():
        raise argparse.ArgumentTypeError(f'"{path}" is not a file')

    return {
        'type': type,
        'path': path
    }


_valid_types = sorted({
    p.stem.split('-')[0] for p in
    (Path(__file__).parent /
     'ingest_validation_tools' /
     'directory-schemas').iterdir()
})


def main():
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
    mutex_group = parser.add_mutually_exclusive_group()
    mutex_group.add_argument(
        '--local_directory', type=_dir_path,
        metavar='PATH',
        help='Local directory to validate')
    mutex_group.add_argument(
        '--globus_url', type=_globus_url,
        metavar='URL',
        help='The Globus File Manager URL of a directory to validate.')
    mutex_group.add_argument(
        '--globus_origin_directory', type=_origin_directory_pair,
        metavar='ORIGIN_PATH',
        help='A Globus submission directory to validate; '
        'Should have the form "<globus_origin_id>:<globus_path>".')

    expected_type_metadata_form = \
        f'<{"|".join(_valid_types)}>:<local_path_to_tsv>'
    parser.add_argument(
        '--type_metadata', type=_type_metadata_pair, nargs='+',
        metavar='TYPE_PATH',
        help='A list of type / metadata.tsv pairs '
        f'of the form "{expected_type_metadata_form}".')

    log_levels = ['DEBUG', 'INFO', 'WARN']
    parser.add_argument(
        '--logging', type=str,
        metavar='LOG_LEVEL',
        help=f'Logging level: One of {log_levels}',
        choices=log_levels,
        default='WARN')

    args = parser.parse_args()
    if not any([
        args.local_directory,
        args.globus_url,
        args.globus_origin_directory,
        args.type_metadata
    ]):
        raise ValidationException('At least one argument is required')

    logging.basicConfig(level=args.logging)

    if args.globus_origin_directory or args.globus_url:
        origin_directory = args.globus_url if args.globus_url \
            else args.globus_origin_directory
        _check_globus_connection(origin_directory['origin'])

    if origin_directory:
        raise ValidationException('TODO: Globus not yet supported')
        # TODO: mirror directory to local cache.

    if args.local_directory:
        logging.info(f'Validating {args.local_directory}')
        messages = _validate_submission_directory_messages(
            args.local_directory)

    if args.type_metadata:
        messages = []
        for type_path in args.type_metadata:
            logging.info(f'Validating {type_path}')
            messages += _validate_metadata_tsv_messages(
                type=type_path['type'],
                metadata_path=type_path['path']
            )
    print('\n'.join(messages))

    return 1 if messages else 0


def _check_globus_connection(origin):
    try:
        subprocess.run(
            ['globus', 'whoami'], check=True,
            stdout=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        raise ValidationException('Run "globus login"')

    try:
        subprocess.run(
            ['globus', 'ls', origin], check=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        raise ValidationException(e.stdout.decode('utf-8'))


def _validate_metadata_tsv_messages(type, metadata_path):
    try:
        validate_metadata_tsv(type=type, metadata_path=metadata_path)
        logging.info('PASS')
        return []
    except TableValidationErrors as e:
        logging.warning('FAIL')
        return [str(e)]


def _validate_data_path_messages(type, data_path):
    logging.info(f'Validating {type} {data_path}')
    try:
        validate_data_path(type=type, data_path=data_path)
        logging.info('PASS')
        return []
    except DirectoryValidationErrors as e:
        logging.warning('FAIL')
        return [str(e)]


def _validate_submission_directory_messages(submission_directory):
    metadata_glob = submission_directory + '/*-metadata.tsv'
    metadata_tsvs = glob(metadata_glob)
    if not metadata_tsvs:
        raise ValidationException(f'Nothing matched {metadata_glob}')
    messages = []
    for tsv_path in metadata_tsvs:
        dir_type = re.match(r'(.+)-metadata\.tsv$', Path(tsv_path).name)[1]
        table_type = dir_type.split('-')[0]
        messages += _validate_metadata_tsv_messages(table_type, tsv_path)

        with open(tsv_path) as f:
            rows = list(csv.DictReader(f, dialect='excel-tab'))
            if not rows:
                raise ValidationException(f'{tsv_path} is empty')
            for row in rows:
                full_data_path = Path(submission_directory) / row['data_path']
                messages += _validate_data_path_messages(
                    dir_type, full_data_path)

    return messages


class ValidationException(Exception):
    # Throw this when there it a problem with the validation process
    # (not just that validation failed) an you don't want a stack trace.
    pass


def _print_message(
        dir, type,
        periods=False, skip_data_path=False):
    # Doctests choke on blank lines: periods=True replaces with "." for now.
    try:
        validate(dir, type, skip_data_path=skip_data_path)
        logging.info('PASS')
        return 0
    except DirectoryValidationErrors as e:
        message = str(e)
        if periods:
            message = re.sub(r'\n(\s*\n)+', '\n.\n', message).strip()
        # End user just wants a name, and doesn't care about refs.
        message = re.sub(r"\$ref: '#/definitions/(\w+)'", r'\1', message)
        # Ad hoc rewrites: Perhaps move these up to the library?
        message = message.replace(
            'fails this "oneOf" check',
            'should be one of these')
        message = message.replace(
            'fails this "contains" check',
            'should contain')

        print(message)
        logging.warning('FAIL')
        return 1
    except TableValidationErrors as e:
        message = str(e)
        if periods:
            message = re.sub(r'\n(\s*\n)+', '\n.\n', message).strip()
        print(message)
        logging.warning('FAIL')
        return 2


if __name__ == "__main__":
    try:
        exit_status = main()
    except ValidationException as e:
        print(e, file=sys.stderr)
        sys.exit(2)
    sys.exit(exit_status)
