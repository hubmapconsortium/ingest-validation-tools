#!/usr/bin/env python3

import csv
import sys
import argparse
from pathlib import Path
import codecs


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
        r = print_encoding_test(args.encoding_test)
    if args.tsv_path:
        r = print_clean_tsv(args.tsv_path)
    return r


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

    # For Python 3.7 and above, this is cleaner:
    #    sys.stdout.reconfigure(encoding=encoding)
    sys.stdout = codecs.getwriter(encoding)(sys.stdout.detach())

    # Header:
    print(
        'quoted', 'empty', 'padded',
        '',  # Empty column header: should be cleaned up!
        sep='\t'
    )

    # Body:
    print(
        f'"{padding}123{padding}"',
        '',
        f'{padding}123{padding}',
        '', '',  # Two empty cells: should be cleaned up!
        sep='\t',
    )
    print(
        '', '', '', '',  # More empty cells: should be cleaned up!
        sep='\t'
    )
    # Trailing \n means there's a trailing empty line in the TSV to clean up.
    return 0


def print_clean_tsv(tsv_path):
    dialect = 'excel-tab'
    writer = csv.writer(sys.stdout, dialect=dialect)

    for encoding in ['utf-8', 'latin-1']:
        warn(f'Trying to read {tsv_path} as {encoding}...')
        try:
            # Read the file completely to determine if there are encoding problems,
            # rather than reading and writing line-by-line.
            rows = csv_to_rows(tsv_path, encoding=encoding, dialect=dialect)
            clean_rows = clean(rows)
            for row in clean_rows:
                writer.writerow(row)
            warn('Read succeeded')
            return 0
        except UnicodeDecodeError as e:
            warn(f'Read failed: {e}')
            continue
    return 1


def csv_to_rows(tsv_path, encoding=None, dialect=None):
    rows = []
    with tsv_path.open(encoding=encoding) as f:
        for row in csv.reader(f, dialect=dialect):
            rows.append(row)
    return rows


def clean(rows):
    '''
    >>> clean([
    ...     ['  x', 'y  ', ''],
    ...     ['', '  Hi!  ', '', ''],
    ...     ['', ''],
    ...     []
    ... ])
    [['x', 'y'], ['', 'Hi!']]

    '''
    clean_rows = []
    max_i = None
    for row in rows:
        stripped_row = [val.strip() for val in row]
        if not any(stripped_row):
            continue
        if max_i is None:
            max_i = last_non_empty_index(stripped_row)
        clean_rows.append(stripped_row[:max_i+1])
    return clean_rows


def last_non_empty_index(values):
    '''
    >>> last_non_empty_index(['', '', '0', '', ''])
    2

    '''
    return max(i for i, val in enumerate(values) if len(val))


def warn(s):
    print(s, file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main())
