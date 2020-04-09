#!/usr/bin/env python

import argparse
import sys
import os
import re
import logging
from pathlib import Path
import subprocess
from glob import glob
import csv

from directory_schema.errors import DirectoryValidationErrors

from hubmap_ingest_validator.validator \
    import validate, validate_metadata_tsv, TableValidationErrors


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

    if not re.match(r'[0-9a-f-]{36}', origin):
        raise argparse.ArgumentTypeError('Orgin format wrong')

    try:
        subprocess.run(
            ['globus', 'whoami'], check=True,
            stdout=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        raise argparse.ArgumentTypeError('Run "globus login"')

    try:
        subprocess.run(
            ['globus', 'ls', s], check=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        raise argparse.ArgumentTypeError(e.stdout.decode('utf-8'))

    return {
        'origin': origin,
        'path': path
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
    (Path(__file__).parent / 'hubmap_ingest_validator'
     / 'directory-schemas' / 'datasets').iterdir()
})


def main():
    parser = argparse.ArgumentParser(
        description='''
Validate a HuBMAP submission, both the metadata TSVs, and the datasets,
either local or remote, or a combination of the two.''',
        epilog='''
Typical usecases:

  --type_metadata + --globus_origin_directory: Validate one or more
  local metadata.tsv files against a submission directory already on Globus.

  --globus_origin_directory: Validate a submission directory on Globus,
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
    # TODO: Parse globus URL.
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

    parser.add_argument(
        '--logging', type=str,
        metavar='LOG_LEVEL',
        choices=['DEBUG', 'INFO', 'WARN'],
        default='WARN')

    args = parser.parse_args()
    if not args.local_directory \
            and not args.globus_origin_directory \
            and not args.type_metadata:
        raise ValidationException('At least one argument is required')

    logging.basicConfig(level=args.logging)

    if args.globus_origin_directory:
        raise ValidationException('TODO: Globus not yet supported')
        # TODO: mirror directory to local cache.

    if args.local_directory:
        logging.info(f'Validating {args.local_directory}')
        messages = _validate_submission_directory_messages(args.local_directory)

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
    # TODO
    return []


def _validate_submission_directory_messages(submission_directory):
    metadata_glob = f'{submission_directory}/*-metadata.tsv'
    metadata_tsvs = glob(metadata_glob)
    if not metadata_tsvs:
        raise ValidationException(f'Nothing matched {metadata_glob}')
    messages = []
    for tsv_path in metadata_tsvs:
        type = re.match(r'(.+)-metadata\.tsv$', Path(tsv_path).name)[1]
        messages += _validate_metadata_tsv_messages(type, tsv_path)

        with open(tsv_path) as f:
            for row in csv.DictReader(f, dialect='excel-tab'):
                messages += _validate_data_path_messages(type, row['data_path'])

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
