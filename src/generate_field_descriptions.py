#!/usr/bin/env python3
import sys
from yaml import dump as dump_yaml
from ingest_validation_tools.schema_loader import (
    list_schema_versions, get_table_schema, get_other_schema
)


def main():
    mapping = {}
    for schema_version in list_schema_versions():
        schema_name = schema_version.schema_name
        # TODO: move this check into get_table_schema()
        get_schema = get_other_schema \
            if schema_name in ['donor', 'sample', 'antibodies', 'contributors'] \
            else get_table_schema
        schema = get_schema(schema_version.schema_name, schema_version.version)
        _add_field_descriptions_to_mapping(schema['fields'], mapping)

    sample_schema = get_other_schema('sample', 0)  # TODO: get latest version
    _add_field_descriptions_to_mapping(sample_schema['fields'], mapping)

    donor_schema = get_other_schema('donor', 0)  # TODO: get latest version
    _add_field_descriptions_to_mapping(donor_schema['fields'], mapping)

    print(dump_yaml(mapping))
    return 0


def _add_field_descriptions_to_mapping(fields, mapping):
    for field in fields:
        name = field['name']
        description = field['description']
        if name in mapping and len(mapping[name]) < len(description):
            # We want to keep the shortest description,
            # on the assumption that it is the most general.
            # In the portal we are not currently passing through the type.
            continue
        mapping[name] = description


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
