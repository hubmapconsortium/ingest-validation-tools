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
    args = parser.parse_args()
    try:
        validate(args.dir, args.type)
    except Exception as e:
        print(e)
        return 1


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
