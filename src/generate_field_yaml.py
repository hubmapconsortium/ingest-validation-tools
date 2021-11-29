#!/usr/bin/env python3
import sys
from yaml import dump as dump_yaml
from collections import defaultdict
import argparse

from ingest_validation_tools.schema_loader import (
    list_schema_versions, get_table_schema, get_other_schema, get_is_assay
)


def main():
    parser = argparse.ArgumentParser(
        description='Outputs a YAML dict listing fields and their definitions, or their types.')
    parser.add_argument(
        '--attr', required=True, choices=['description', 'type', 'assay', 'entity'],
        help='Attribute to pull from schemas')
    args = parser.parse_args()

    default_value = 'string' if args.attr == 'type' else None
    mapping = defaultdict(set) if args.attr == 'assay' else {}

    for schema_version in list_schema_versions():
        schema_name = schema_version.schema_name
        get_schema = get_table_schema if get_is_assay(schema_name) else get_other_schema
        schema = get_schema(schema_version.schema_name, schema_version.version)
        for field in schema['fields']:
            name = field['name']
            attr_value = field.get(args.attr, default_value)
            if args.attr == 'description':
                if name in mapping and len(mapping[name]) < len(attr_value):
                    # We want to keep the shortest description,
                    # on the assumption that it is the most general.
                    continue
                mapping[name] = attr_value
            elif args.attr == 'type':
                if name in mapping and mapping[name] != attr_value:
                    raise Exception(
                        f'Inconsistent types for {name}: "{mapping[name]}" != "{attr_value}"')
                mapping[name] = attr_value
            elif args.attr == 'entity':
                if name == 'version':
                    continue
                attr_value = 'assay' if get_is_assay(schema_name) else schema_name
                if name in mapping and mapping[name] != attr_value:
                    raise Exception(
                        f'Inconsistent types for {name}: "{mapping[name]}" != "{attr_value}"')
                mapping[name] = attr_value
            elif args.attr == 'assay':
                # TODO: Move these out:
                assay_type_fields = [f for f in schema['fields'] if f['name'] == 'assay_type']
                if len(assay_type_fields) == 0:
                    continue
                assay_type_field = assay_type_fields[0]
                assays = assay_type_field['constraints']['enum']
                mapping[name] |= set(assays)

    mapping = {k: sorted(list(v)) for k, v in mapping.items()} if args.attr == 'assay' else mapping
    print(dump_yaml(mapping))
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
