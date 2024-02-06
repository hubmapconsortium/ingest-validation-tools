#!/usr/bin/env python3

import argparse
import csv
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="""
Use the "--tsv_in"/"--tsv_out" options to strip invisible characters from TSVs.
"""
    )
    mutex = parser.add_mutually_exclusive_group(required=True)
    mutex.add_argument(
        "--tsv_in", type=Path, metavar="INPUT", help="TSV to strip padding whitespace from"
    )
    mutex.add_argument(
        "--encoding_test",
        type=str,
        metavar="ENCODING",
        help="Generate test TSV using this encoding",
    )
    parser.add_argument(
        "--tsv_out", type=Path, metavar="OUTPUT", help="Destination for clean TSV", required=True
    )
    args = parser.parse_args()

    if args.encoding_test:
        r = print_encoding_test(args.encoding_test, args.tsv_out)
    if args.tsv_in:
        r = print_clean_tsv(args.tsv_in, args.tsv_out)
    return r


def print_encoding_test(encoding, output_path):
    space_chars = [
        "\u000b",  # vertical tab
        "\u0020",  # normal space
    ]
    if encoding != "ascii":
        space_chars += [
            "\u00a0",  # non-breaking space
        ]
    if encoding not in ["ascii", "latin-1"]:
        space_chars += [
            "\u2003",  # em space
            "\u3000",  # idiographic space
        ]
    padding = "".join(space_chars)

    with output_path.open(mode="w", encoding=encoding) as f:
        # Header:
        print(
            "quoted",
            "empty",
            "padded",
            "",  # Empty column header: should be cleaned up!
            sep="\t",
            file=f,
        )

        # Body:
        print(
            f'"{padding}123{padding}"',
            "",
            f"{padding}123{padding}",
            "",
            "",  # Two empty cells: should be cleaned up!
            sep="\t",
            file=f,
        )
        print("", "", "", "", sep="\t", file=f)  # More empty cells: should be cleaned up!
    # Trailing \n means there's a trailing empty line in the TSV to clean up.
    return 0


def print_clean_tsv(input_path, output_path):
    dialect = "excel-tab"
    writer = csv.writer(output_path.open(mode="w", newline=""), dialect=dialect)

    for encoding in ["utf-8", "latin-1"]:
        warn(f"Trying to read {input_path} as {encoding}...")
        try:
            # Read the file completely to determine if there are encoding problems,
            # rather than reading and writing line-by-line.
            rows = csv_to_rows(input_path, encoding=encoding, dialect=dialect)
            clean_rows = clean(rows)
            for row in clean_rows:
                writer.writerow(row)
            warn("Read succeeded")
            return 0
        except UnicodeDecodeError as e:
            warn(f"Read failed: {e}")
            continue
    return 1


def csv_to_rows(tsv_path, encoding=None, dialect=None):
    rows = []
    with tsv_path.open(encoding=encoding) as f:
        for row in csv.reader(f, dialect=dialect):
            rows.append(row)
    return rows


def clean(rows):
    """
    >>> clean([
    ...     ['  x', 'y  ', ''],
    ...     ['', '  Hi!  ', '', ''],
    ...     ['', ''],
    ...     []
    ... ])
    [['x', 'y'], ['', 'Hi!']]

    """
    clean_rows = []
    max_i = None
    for row in rows:
        stripped_row = [val.strip() for val in row]
        if not any(stripped_row):
            continue
        if max_i is None:
            max_i = last_non_empty_index(stripped_row)
        clean_rows.append(stripped_row[: max_i + 1])
    return clean_rows


def last_non_empty_index(values):
    """
    >>> last_non_empty_index(['', '', '0', '', ''])
    2

    """
    return max(i for i, val in enumerate(values) if len(val))


def warn(s):
    print(s, file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main())
