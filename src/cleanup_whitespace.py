#!/usr/bin/env python3

import csv
import sys
import argparse

from yaml import dump as dump_yaml


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'tsv_path',
        type=argparse.FileType('r', encoding='utf-8'),
        help='TSV to strip padding whitespace from')
    args = parser.parse_args()

    dialect = 'excel-tab'
    writer = csv.writer(sys.stdout, dialect=dialect)

    # There could be whitespace inside the quoted value,
    # so we really do need to parse it as a tsv.
    for row in csv.reader(args.tsv_path, dialect=dialect):
        writer.writerow(val.strip() for val in row)

    return 0


if __name__ == "__main__":
    sys.exit(main())
