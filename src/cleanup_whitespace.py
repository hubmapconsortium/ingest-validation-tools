#!/usr/bin/env python3

import csv
import sys
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description='''
Data providers may use the "--tsv_path" option to strip invisible characters from TSVs.
The cleaned TSV is printed to STDOUT: Use output redirection to save.'''
    )
    mutex = parser.add_mutually_exclusive_group(required=True)
    mutex.add_argument(
        '--tsv_path',
        type=Path,
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
        print_clean_tsv(args.tsv_path)
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


def print_clean_tsv(tsv_path):
    dialect = 'excel-tab'
    writer = csv.writer(sys.stdout, dialect=dialect)

    for encoding in ['utf-8', 'latin-1']:
        warn(f'Trying to read {tsv_path} as {encoding}...')
        try:
            with tsv_path.open(encoding=encoding) as f:
                # There could be whitespace inside the quoted value,
                # so we really do need to parse it as a tsv,
                # and can't just use a regex.
                for row in csv.reader(f, dialect=dialect):
                    writer.writerow(val.strip() for val in row)
            warn('Read succeeded')
            return
        except UnicodeDecodeError as e:
            warn(f'Read failed: {e}')
            continue


def warn(s):
    print(s, file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main())
