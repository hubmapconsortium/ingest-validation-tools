#!/usr/bin/env python3
import sys
from yaml import dump as dump_yaml
import argparse

from ingest_validation_tools.schema_loader import (
    list_table_schema_versions,
    get_table_schema,
    get_is_assay,
)


def main():
    parser = argparse.ArgumentParser(
        description="Outputs a YAML dict listing fields and their definitions, or their types."
    )
    parser.add_argument(
        "--attr",
        required=True,
        choices=["description", "type", "assay", "entity", "schema"],
        help="Attribute to pull from schemas",
    )
    args = parser.parse_args()

    mapper = make_mapper(args.attr)
    for schema_version in list_table_schema_versions():
        schema = get_table_schema(schema_version)
        for field in schema["fields"]:
            mapper.add(field, schema_name=schema_version.schema_name, schema=schema)
    print(mapper.dump_yaml())
    return 0


def make_mapper(attr):
    return {
        "description": DescriptionMapper,
        "type": TypeMapper,
        "assay": AssayMapper,
        "entity": EntityMapper,
        "schema": SchemaMapper,
    }[attr]()


class Mapper:
    def __init__(self):
        self.mapping = {}
        self.default_value = None

    def add(self, field, schema_name=None, schema=None):
        name, attr_value = self._get_name_value(
            field, schema_name=schema_name, schema=schema
        )
        if self._skip_field(name, attr_value):
            return
        if name in self.mapping and self.mapping[name] != attr_value:
            self._handle_collision(name, attr_value)
        else:
            self.mapping[name] = attr_value

    def _get_name_value(self, field, **kwargs):
        name = field["name"]
        attr_value = field.get(self.attr, self.default_value)
        return name, attr_value

    def _skip_field(self, name, attr_value):
        return False

    def _handle_collision(self, name, attr_value):
        raise Exception(
            f'{name} is inconsistent: "{self.mapping[name]}" != "{attr_value}"'
        )

    def dump_yaml(self):
        return dump_yaml(self.mapping)


class DescriptionMapper(Mapper):
    """
    >>> mapper = DescriptionMapper()
    >>> mapper.add({'name': 'field_name', 'description': 'long description'})
    >>> mapper.add({'name': 'field_name', 'description': 'short desc'})
    >>> mapper.add({'name': 'field_name', 'description': 'longer description'})
    >>> print(mapper.dump_yaml().strip())
    field_name: short desc
    """

    def __init__(self):
        super().__init__()
        self.attr = "description"

    def _handle_collision(self, name, attr_value):
        if len(attr_value) < len(self.mapping[name]):
            # Assuming the shorter string will be more generic...
            self.mapping[name] = attr_value


class TypeMapper(Mapper):
    """
    >>> mapper = TypeMapper()
    >>> mapper.add({'name': 'explicit', 'type': 'fake_type'})
    >>> mapper.add({'name': 'implicit'})
    >>> print(mapper.dump_yaml().strip())
    explicit: fake_type
    implicit: string
    """

    def __init__(self):
        super().__init__()
        self.attr = "type"
        self.default_value = "string"


class AbstractSetValuedMapper(Mapper):
    def _skip_field(self, name, attr_value):
        return len(attr_value) == 0

    def _handle_collision(self, name, attr_value):
        self.mapping[name] |= attr_value

    def dump_yaml(self):
        return dump_yaml({k: sorted(list(v)) for k, v in self.mapping.items()})


class EntityMapper(AbstractSetValuedMapper):
    """
    >>> mapper = EntityMapper()
    >>> mapper.add({'name': 'dataset_field'}, schema_name='default_is_dataset')
    >>> mapper.add({'name': 'sample_field'}, schema_name='sample')
    >>> mapper.add({'name': 'sample_block_field'}, schema_name='sample-block')
    >>> print(mapper.dump_yaml().strip())
    dataset_field:
    - dataset
    sample_block_field:
    - sample
    sample_field:
    - sample
    """

    def _get_name_value(self, field, schema_name=None, schema=None):
        name = field["name"]
        entity = "dataset" if get_is_assay(schema_name) else schema_name.split("-")[0]
        return name, set([entity])


class AssayMapper(AbstractSetValuedMapper):
    """
    >>> mapper = AssayMapper()
    >>> schema_a = {
    ...     'fields': [{
    ...         'name': 'assay_type',
    ...         'constraints': {'enum': ['A']}
    ...     }]
    ... }
    >>> schema_b = {
    ...     'fields': [{
    ...         'name': 'assay_type',
    ...         'constraints': {'enum': ['B']}
    ...     }]
    ... }
    >>> schema_other = {
    ...     'fields': []
    ... }
    >>> mapper.add({'name': 'in_both'}, schema=schema_a)
    >>> mapper.add({'name': 'in_both'}, schema=schema_b)
    >>> mapper.add({'name': 'in_other'}, schema=schema_other)
    >>> print(mapper.dump_yaml().strip())
    in_both:
    - A
    - B
    """

    def _get_name_value(self, field, schema_name=None, schema=None):
        assay_type_fields = [
            field for field in schema["fields"] if field["name"] == "assay_type"
        ]
        value = (
            assay_type_fields[0]["constraints"]["enum"]
            if len(assay_type_fields)
            else []
        )
        return field["name"], set(value)


class SchemaMapper(AbstractSetValuedMapper):
    """
    >>> mapper = SchemaMapper()
    >>> mapper.add({'name': 'ab_field'}, schema_name='A')
    >>> mapper.add({'name': 'ab_field'}, schema_name='B')
    >>> mapper.add({'name': 'c_field'}, schema_name='C')
    >>> print(mapper.dump_yaml().strip())
    ab_field:
    - A
    - B
    c_field:
    - C
    """

    def _get_name_value(self, field, schema_name=None, schema=None):
        return field["name"], {schema_name}


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
