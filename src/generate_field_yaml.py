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

    if args.attr == 'description':
        mapper = DescriptionMapper()
    if args.attr == 'type':
        mapper = TypeMapper()
    if args.attr == 'assay':
        mapper = AssayMapper()
    if args.attr == 'entity':
        mapper = EntityMapper()

    for schema_version in list_schema_versions():
        schema_name = schema_version.schema_name
        get_schema = get_table_schema if get_is_assay(schema_name) else get_other_schema
        schema = get_schema(schema_version.schema_name, schema_version.version)
        for field in schema['fields']:
            mapper.add(field, schema_name)
    print(mapper.dump_yaml())
    return 0


class Mapper:
    def __init__(self):
        self.mapping = {}
        self.default_value = None
    def add(self, field, schema_name):
        name, attr_value = self._get_name_value(field, schema_name)
        if name is None:
            return
        if name in self.mapping and self.mapping[name] != attr_value:
            self._handle_collision(name, attr_value)
        else:
            self.mapping[name] = self._new_mapping(attr_value)
    def _get_name_value(self, field, schema_name):
        name = field['name']
        attr_value = field.get(self.attr, self.default_value)
        return name, attr_value
    def _handle_collision(self, name, attr_value):
        raise Exception(
            f'{name} is inconsistent: "{self.mapping[name]}" != "{attr_value}"')
    def _new_mapping(self, attr_value):
        return attr_value
    def dump_yaml(self):
        return dump_yaml(self.mapping)


class DescriptionMapper(Mapper):
    def __init__(self):
        super().__init__()
        self.attr = 'description'
    def _handle_collision(self, name, attr_value):
        if len(attr_value) < len(self.mapping[name]):
            # Assuming the shorter string will be more generic...
            self.mapping[name] = attr_value


class TypeMapper(Mapper):
    def __init__(self):
        super().__init__()
        self.attr = 'type'
        self.default_value = 'string'


class EntityMapper(Mapper):
    def _get_name_value(self, field, schema_name):
        name = field['name']
        if name == 'version':
            # The version field is unique in that it occurs in multiple
            # entity types: Seems easiest just to skip it,
            # rather than changing value from string to list
            return None, None
        return name, 'assay' if get_is_assay(schema_name) else schema_name


class AssayMapper(Mapper):
    # TODO
    def _handle_collision(self, name, attr_value):
        self.mapping[name] |= attr_value
    def _new_mapping(self, attr_value):
        return set(attr_value)
    def dump_yaml(self):
        dump_yaml({k: sorted(list(v)) for k, v in self.mapping.items()})

if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
