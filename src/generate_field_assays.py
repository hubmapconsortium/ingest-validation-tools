#!/usr/bin/env python3
import sys
from yaml import dump as dump_yaml
import argparse
from collections import defaultdict

from ingest_validation_tools.schema_loader import (
    list_schema_versions, get_table_schema, get_is_assay
)


def main():
    parser = argparse.ArgumentParser(
        description='Outputs a YAML dict listing fields and the assays where they are used.')
    parser.parse_args()

    mapping = defaultdict(set)
    for schema_version in list_schema_versions():
        schema_name = schema_version.schema_name
        if not get_is_assay(schema_name):
            continue
        schema = get_table_schema(schema_version.schema_name, schema_version.version)
        _add_field_assays_to_mapping(schema['fields'], mapping)
    print(dump_yaml({k: sorted(list(v)) for k, v in mapping.items()}))
    return 0


def _add_field_assays_to_mapping(fields, mapping):
    assay_type_field = [f for f in fields if f['name'] == 'assay_type'][0]
    assays = assay_type_field['constraints']['enum']
    for field in fields:
        name = field['name']
        mapping[name] |= set(assays)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
