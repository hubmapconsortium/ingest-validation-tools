#!/usr/bin/env python3

import sys
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description='''
    Factor out all variants of a given field. Typical use:

    src/factor_field.py \\
        --field resolution_z_value \\
        --input_dir src/ingest_validation_tools/table-schemas/assays/ \\
        --output_dir src/ingest_validation_tools/table-schemas/includes/fields
    ''')
    parser.add_argument(
        '--field',
        metavar='NAME',
        required=True)
    parser.add_argument(
        '--input_dir',
        type=Path,
        metavar='IN',
        help='Directory to scan for instances of the field',
        required=True)
    parser.add_argument(
        '--output_dir',
        type=Path,
        metavar='OUT',
        help='Directory to write field extracts',
        required=True)
    args = parser.parse_args()

    factor_field(args.field, args.input_dir, args.output_dir)
    return 0


def factor_field(field, input_dir, output_dir):
    print(field, input_dir, output_dir)


if __name__ == "__main__":
    sys.exit(main())
