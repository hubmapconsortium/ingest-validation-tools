#!/usr/bin/env python3
import sys
from csv import DictWriter

from ingest_validation_tools.schema_loader import (
    list_types, get_table_schema, get_other_schema
)


def main():
    fieldnames = ['filename', 'field', 'description', 'enum']
    writer = DictWriter(sys.stdout, fieldnames=fieldnames)
    writer.writeheader()
    for assay_type in list_types():
        filename = f'{assay_type}.yaml'
        schema = get_table_schema(assay_type)
        for field in schema['fields']:
            if 'constraints' in field and 'enum' in field['constraints']:
                enums = field['constraints']['enum']
            else:
                enums = ['']
            for enum in enums:
                writer.writerow({
                    'filename': filename,
                    'field': field['name'],
                    'description': field['description'],
                    'enum': enum
                })
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
