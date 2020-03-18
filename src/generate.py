#!/usr/bin/env python

import argparse
from pathlib import Path
import sys

from yaml import safe_load as load_yaml

_schemas_path = (
    Path(__file__).parent / 'hubmap_ingest_validator' / 'table-schemas'
)


def main():
    valid_types = [p.stem for p in _schemas_path.iterdir()]

    parser = argparse.ArgumentParser()
    parser.add_argument(
        'type', metavar='TYPE', type=str,
        choices=valid_types,
        help='Template to generate')
    args = parser.parse_args()
    print(_generate_csv_template(args.type))


def _generate_csv_template(type):
    schema_path = _schemas_path / f'{type}.yaml'
    schema = load_yaml(open(schema_path).read())
    names = [field['name'] for field in schema['fields']]
    return '\t'.join(names) + '\n'


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
