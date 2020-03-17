#!/usr/bin/env python

import argparse
import sys
import os
import logging

from directory_schema.errors import DirectoryValidationErrors

from validator import validate


def dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise Exception(f'"{string}" is not a directory')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'dir', metavar='DIRECTORY', type=dir_path,
        help='Directory to validate')
    parser.add_argument(
        'type', metavar='TYPE', type=str,
        help='Ingest data type')
    parser.add_argument(
        '--logging', metavar='LOG_LEVEL', type=str,
        choices=['DEBUG', 'INFO', 'WARN'],
        default='WARN')
    args = parser.parse_args()
    logging.basicConfig(level=args.logging)
    try:
        validate(args.dir, args.type)
        logging.info('PASS')
    except DirectoryValidationErrors as e:
        print(e)
        logging.warning('FAIL')
        return 1


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
