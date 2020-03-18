#!/usr/bin/env python

import argparse
from pathlib import Path
import sys

from yaml import safe_load as load_yaml


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'type', metavar='TYPE', type=str,
        help='Template to generate')
    args = parser.parse_args()
    print(generate_csv_template(args.type))


def generate_csv_template(type):
    schema_path = (Path(__file__).parent / 'hubmap_ingest_validator'
                   / 'table-schemas' / f'{type}.yaml')
    schema = load_yaml(open(schema_path).read())
    names = [field['name'] for field in schema['fields']]
    return '\t'.join(names) + '\n'


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
