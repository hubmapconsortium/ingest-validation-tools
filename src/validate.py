#!/usr/bin/env python

import argparse
import sys
import os
import re
import logging
from pathlib import Path
from string import ascii_uppercase

from directory_schema.errors import DirectoryValidationErrors

from hubmap_ingest_validator.validator import validate, TableValidationErrors


def _dir_path(s):
    if os.path.isdir(s):
        return s
    else:
        raise Exception(f'"{s}" is not a directory')


def _origin_directory_pair(s):
    return s


def _type_metadata_pair(s):
    return s


def main():
    valid_types = sorted([
        p.stem for p in
        (Path(__file__).parent / 'hubmap_ingest_validator'
         / 'directory-schemas' / 'datasets').iterdir()
    ])

    parser = argparse.ArgumentParser()
    mutex_group = parser.add_mutually_exclusive_group()
    mutex_group.add_argument(
        '--local_directory', type=_dir_path, metavar='PATH',
        help='Local directory to validate')
    mutex_group.add_argument(
        '--globus_origin_directory', type=_origin_directory_pair, metavar='ORIGIN_PATH',
        help='A string of the form "<globus_origin_id>:<globus_path>')

    parser.add_argument(
        '--type_metadata', type=_type_metadata_pair, nargs='+', metavar='TYPE_PATH',
        help=f'A string of the form "<{"|".join(valid_types)}>:<local_path_to_tsv>"')

    parser.add_argument(
        '--logging', metavar='LOG_LEVEL', type=str,
        choices=['DEBUG', 'INFO', 'WARN'],
        default='WARN')

    args = parser.parse_args()
    logging.basicConfig(level=args.logging)
    return args
    return _print_message(
        args.dir, args.type,
        args.donor_id, args.tissue_id,
        skip_data_path=args.skip_data_path
    )


def _print_message(
        dir, type, donor_id, tissue_id,
        periods=False, skip_data_path=False):
    # Doctests choke on blank lines: periods=True replaces with "." for now.
    try:
        validate(dir, type, donor_id, tissue_id, skip_data_path=skip_data_path)
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
        message = re.sub(
            r'(column) (\d+)',
            lambda m: f'{m[1]} {m[2]} ("{_number_to_letters(m[2])}")',
            message,
            flags=re.I
        )
        print(message)
        logging.warning('FAIL')
        return 2


def _number_to_letters(n):
    '''
    >>> _number_to_letters(1)
    'A'
    >>> _number_to_letters(26)
    'Z'
    >>> _number_to_letters(27)
    'AA'
    >>> _number_to_letters(52)
    'AZ'

    '''
    def n2a(n):
        uc = ascii_uppercase
        d, m = divmod(n, len(uc))
        return n2a(d - 1) + uc[m] if d else uc[m]
    return n2a(int(n) - 1)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
