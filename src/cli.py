#!/usr/bin/env python

import argparse
import sys
import os
import logging

from directory_schema.errors import DirectoryValidationErrors

from hubmap_ingest_validator.validator import validate


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
    return print_message(args.dir, args.type)


def print_message(dir, type):
    try:
        validate(dir, type)
        logging.info('PASS')
        return 0
    except DirectoryValidationErrors as e:
        print(e)
        logging.warning('FAIL')
        return 1


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
