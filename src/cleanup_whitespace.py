#!/usr/bin/env python3

import csv
import sys
import argparse

from yaml import dump as dump_yaml


def main():
    parser = argparse.ArgumentParser()
    mutex = parser.add_mutually_exclusive_group(required=True)
    mutex.add_argument(
        '--tsv_path',
        type=argparse.FileType('r', encoding='utf-8'),
        metavar='PATH',
        help='TSV to strip padding whitespace from')
    mutex.add_argument(
        '--encoding_test',
        type=str,
        metavar='ENCODING',
        help='Generate test TSV using this encoding')
    args = parser.parse_args()

    if args.encoding_test:
        print_encoding_test(args.encoding_test)
    if args.tsv_path:
        print_tsv(args.tsv_path)
    return 0


def print_encoding_test(encoding):
    space_chars = [
        '\u000b',  # vertical tab
        '\u0020',  # normal space
    ]
    if encoding != 'ascii':
        space_chars += [
            '\u00a0',  # non-breaking space
        ]
    if encoding not in ['ascii', 'latin-1']:
        space_chars += [
            '\u2003',  # em space
            '\u3000',  # idiographic space
        ]
    padding = ''.join(space_chars)
    
    sys.stdout.reconfigure(encoding=encoding)

    # Header:
    print(
        'quoted', 'empty', 'padded',
        sep='\t'
    )

    # Body:
    print(
        f'"{padding}123{padding}"',
        '',
        f'{padding}123{padding}',
        sep='\t',
        end=''
    )


def print_tsv(tsv_path):
    dialect = 'excel-tab'
    writer = csv.writer(sys.stdout, dialect=dialect)

    # There could be whitespace inside the quoted value,
    # so we really do need to parse it as a tsv.
    for row in csv.reader(tsv_path, dialect=dialect):
        writer.writerow(val.strip() for val in row)


if __name__ == "__main__":
    sys.exit(main())
