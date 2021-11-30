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
        '--attr', required=True, choices=['description', 'type', 'assay', 'entity'],
        help='Attribute to pull from schemas')
    args = parser.parse_args()

    mapper = make_mapper(args.attr)
    for schema_version in list_schema_versions():
        schema_name = schema_version.schema_name
        get_schema = get_table_schema if get_is_assay(schema_name) else get_other_schema
        schema = get_schema(schema_version.schema_name, schema_version.version)
        for field in schema['fields']:
            mapper.add(field, schema_name=schema_name, schema=schema)
    print(mapper.dump_yaml())
    return 0


def make_mapper(attr):
    return {
        'description': DescriptionMapper,
        'type': TypeMapper,
        'assay': AssayMapper,
        'entity': EntityMapper,
    }[attr]()


class Mapper:
    def __init__(self):
        self.mapping = {}
        self.default_value = None
    def add(self, field, schema_name=None, schema=None):
        name, attr_value = self._get_name_value(field, schema_name=schema_name, schema=schema)
        if self._skip_field(name, attr_value):
            return
        if name in self.mapping and self.mapping[name] != attr_value:
            self._handle_collision(name, attr_value)
        else:
            self.mapping[name] = attr_value
    def _get_name_value(self, field, **kwargs):
        name = field['name']
        attr_value = field.get(self.attr, self.default_value)
        return name, attr_value
    def _skip_field(self, name, attr_value):
        return False
    def _handle_collision(self, name, attr_value):
        raise Exception(
            f'{name} is inconsistent: "{self.mapping[name]}" != "{attr_value}"')
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
    def _skip_field(self, name, attr_value):
        # The version field is unique in that it occurs under multiple
        # entity types: Seems easiest just to skip it,
        # rather than changing value from string to set or list
        return name == 'version'
    def _get_name_value(self, field, schema_name=None, schema=None):
        name = field['name']
        return name, 'assay' if get_is_assay(schema_name) else schema_name


class AssayMapper(Mapper):
    def _get_name_value(self, field, schema_name=None, schema=None):
        assay_type_fields = [
            field for field in schema['fields']
            if field['name'] == 'assay_type'
        ]
        value = (
            assay_type_fields[0]['constraints']['enum']
            if len(assay_type_fields) else []
        )
        return field['name'], set(value)
    def _skip_field(self, name, attr_value):
        return len(attr_value) == 0
    def _handle_collision(self, name, attr_value):
        self.mapping[name] |= attr_value
    def dump_yaml(self):
        return dump_yaml({k: sorted(list(v)) for k, v in self.mapping.items()})


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
