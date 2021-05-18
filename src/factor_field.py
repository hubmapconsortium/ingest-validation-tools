#!/usr/bin/env python3

import sys
import argparse
from pathlib import Path
import fileinput
from collections import defaultdict


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


def factor_field(field_name, input_dir, output_dir):
    definitions = pull(field_name, input_dir)
    push(field_name, definitions, output_dir)


def pull(field_name, input_dir):
    definitions = defaultdict(set)
    with fileinput.input(files=input_dir.iterdir(), inplace=True) as f:
        inside = False
        definition = None
        for line in f:
            # This assumes the YAML has been cleaned up!
            if f'name: {field_name}' in line:
                inside = True
                print(f'# include: ../includes/fields/{field_name}.yaml')
                definition = line
                continue
            elif inside and line[0] != '-':
                definition += line
                continue
            elif inside:
                definitions[definition].add(str(fileinput.filename()))
                inside = False
            print(line, end='')
    return definitions


def push(field_name, definitions, output_dir):
    options = [
        f"# {'; '.join(files)}\n{definition}"
        for definition, files in definitions.items()
    ]
    (output_dir / f'{field_name}.yaml').write_text('\n'.join(options))


if __name__ == "__main__":
    sys.exit(main())
