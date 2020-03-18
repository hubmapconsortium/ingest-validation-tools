#!/usr/bin/env python

import argparse
from pathlib import Path
import sys

from yaml import safe_load as load_yaml, dump as dump_yaml


def main():
    schemas_path = (
        Path(__file__).parent / 'hubmap_ingest_validator' / 'table-schemas'
    )
    valid_types = [p.stem for p in schemas_path.iterdir()]

    parser = argparse.ArgumentParser()
    parser.add_argument(
        'type',
        choices=valid_types,
        help='What type to generate for')
    parser.add_argument(
        'target',
        choices=['template.tsv', 'schema.yaml'],
        help='What kind of thing to generate')
    args = parser.parse_args()

    schema_path = schemas_path / f'{args.type}.yaml'
    table_schema = load_yaml(open(schema_path).read())

    if args.target == 'template.tsv':
        print(_generate_template_tsv(table_schema))
    elif args.target == 'schema.yaml':
        print(_generate_schema_yaml(table_schema))
    elif args.target == 'README.md':
        print(_generate_readme_md(table_schema))


def _generate_template_tsv(table_schema):
    names = [field['name'] for field in table_schema['fields']]
    return '\t'.join(names) + '\n'


def _generate_schema_yaml(table_schema):
    json_schema = {
        'properties': {
            field['name']: {
                'type': 'string',  # TODO: for now...
                'description': field['description']
            } for field in table_schema['fields']
        }
    }
    return dump_yaml(json_schema)


def _generate_readme_md(table_schema):
    pass


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
