#!/usr/bin/env python

import argparse
import sys
import os
import re
import logging
from pathlib import Path

from directory_schema.errors import DirectoryValidationErrors

from hubmap_ingest_validator.validator import validate


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
        'dir', metavar='DIRECTORY', type=_dir_path,
        help='Directory to validate')
    parser.add_argument(
        'type', metavar='TYPE', type=str,
        choices=valid_types,
        help='Ingest data type')
    parser.add_argument(
        '--logging', metavar='LOG_LEVEL', type=str,
        choices=['DEBUG', 'INFO', 'WARN'],
        default='WARN')
    args = parser.parse_args()
    logging.basicConfig(level=args.logging)
    return _print_message(args.dir, args.type)


def _print_message(dir, type):
    try:
        validate(dir, type)
        logging.info('PASS')
        return 0
    except DirectoryValidationErrors as e:
        # Regex is to make the doctests more readable,
        # so we don't need tons of <BLANKLINE>s.
        print(re.sub(r'\n(\s*\n)*', '\n', str(e)))
        logging.warning('FAIL')
        return 1


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
