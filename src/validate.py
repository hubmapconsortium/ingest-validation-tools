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


def _dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise Exception(f'"{string}" is not a directory')


def main():
    valid_types = [
        p.stem for p in
        (Path(__file__).parent / 'hubmap_ingest_validator'
         / 'directory-schemas' / 'datasets').iterdir()
    ]

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--dir', type=_dir_path, required=True,
        help='Directory to validate')
    parser.add_argument(
        '--type', type=str, required=True,
        choices=valid_types,
        help='Ingest data type')
    parser.add_argument(
        '--donor_id', type=str, metavar='ID', required=True,
        help='HuBMAP Display ID of Donor')
    parser.add_argument(
        '--tissue_id', type=str, metavar='ID', required=True,
        help='HuBMAP Display ID of Tissue')
    parser.add_argument(
        '--logging', metavar='LOG_LEVEL', type=str,
        choices=['DEBUG', 'INFO', 'WARN'],
        default='WARN')
    args = parser.parse_args()
    logging.basicConfig(level=args.logging)
    return _print_message(
        args.dir, args.type,
        args.donor_id, args.tissue_id
    )


def _print_message(dir, type, donor_id, tissue_id, periods=False):
    # Doctests choke on blank lines: periods=True replaces with "." for now.
    try:
        validate(dir, type, donor_id, tissue_id)
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
