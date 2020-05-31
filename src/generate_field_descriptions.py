#!/usr/bin/env python3
import sys
from yaml import dump as dump_yaml
from ingest_validation_tools.table_schema_loader import list_types, get_schema


def main():
    mapping = {}
    for assay_type in list_types():
        schema = get_schema(assay_type)
        for field in schema['fields']:
            name = field['name']
            description = field['description']
            if name in mapping and len(mapping[name]) < len(description):
                # We want to keep the shortests description,
                # on the assumption that it is the most general.
                # In the portal we are not currently passing through the type.
                continue
            mapping[name] = description
    print(dump_yaml(mapping))
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
