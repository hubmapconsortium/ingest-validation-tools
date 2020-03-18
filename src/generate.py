#!/usr/bin/env python

import argparse
from pathlib import Path
import sys

from yaml import safe_load as load_yaml, dump as dump_yaml

_schemas_path = (
    Path(__file__).parent / 'hubmap_ingest_validator' / 'table-schemas'
)


def main():
    valid_types = [p.stem for p in _schemas_path.iterdir()]

    parser = argparse.ArgumentParser()
    parser.add_argument(
        'type',
        choices=valid_types,
        help='What type to generate for')
    parser.add_argument(
        'target',
        choices=['template', 'schema'],
        help='What kind of thing to generate')
    args = parser.parse_args()
    if args.target == 'template':
        print(_generate_csv_template(args.type))
    elif args.target == 'schema':
        print(_generate_json_schema(args.type))


def _generate_csv_template(type):
    schema_path = _schemas_path / f'{type}.yaml'
    table_schema = load_yaml(open(schema_path).read())
    names = [field['name'] for field in table_schema['fields']]
    return '\t'.join(names) + '\n'


def _generate_json_schema(type):
    schema_path = _schemas_path / f'{type}.yaml'
    table_schema = load_yaml(open(schema_path).read())
    json_schema = {
        'properties': {
            field['name']: {
                'type': 'string',  # TODO: for now...
                'description': field['description']
            } for field in table_schema['fields']
        }
    }
    return dump_yaml(json_schema)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
