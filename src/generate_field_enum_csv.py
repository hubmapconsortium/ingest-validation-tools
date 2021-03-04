#!/usr/bin/env python3
import sys
from csv import DictWriter
import argparse

from ingest_validation_tools.schema_loader import (
    list_types, get_table_schema
)


def main():
    default_fields = ['filename', 'field', 'description', 'enum']
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--fields',
        default=default_fields,
        nargs='+',
        metavar='FIELD',
        help=f'Fields to include in report. Default: {default_fields}')
    args = parser.parse_args()

    writer = DictWriter(sys.stdout, fieldnames=args.fields)
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
