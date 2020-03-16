#!/usr/bin/env python

import argparse
import sys
import os

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
        '-v', action='store_true',
        help='Verbose')
    args = parser.parse_args()
    try:
        validate(args.dir, args.type)
        if (args.v):
            print('PASS')
    except Exception as e:
        if (args.v):
            print('FAIL')
        print(e)
        return 1


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
