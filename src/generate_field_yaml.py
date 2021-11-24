#!/usr/bin/env python3
import sys
from yaml import dump as dump_yaml
import argparse

from ingest_validation_tools.schema_loader import (
    list_schema_versions, get_table_schema, get_other_schema, get_is_assay
)


def main():
    parser = argparse.ArgumentParser(
        description='Outputs a YAML dict listing fields and their definitions, or their types.')
    parser.add_argument(
        '--attr', required=True, choices=['description', 'type'],
        help='Attribute to pull from schemas')
    args = parser.parse_args()

    mapping = {}
    for schema_version in list_schema_versions():
        schema_name = schema_version.schema_name
        get_schema = get_table_schema if get_is_assay(schema_name) else get_other_schema
        schema = get_schema(schema_version.schema_name, schema_version.version)
        for field in schema['fields']:
            name = field['name']
            attr_value = field.get(args.attr, 'string' if args.attr == 'type' else None)
            if args.attr == 'description':
                if name in mapping and len(mapping[name]) < len(attr_value):
                    # We want to keep the shortest description,
                    # on the assumption that it is the most general.
                    continue
            elif args.attr == 'type':
                if name in mapping and mapping[name] != attr_value:
                    raise Exception(
                        f'Inconsistent types for {name}: "{mapping[name]}" != "{attr_value}"')
            else:
                raise Exception(f'argparse should not have allowed {args.attr}')
            mapping[name] = attr_value
    print(dump_yaml(mapping))
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
