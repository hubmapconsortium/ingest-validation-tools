#!/usr/bin/env python3

import argparse
from pathlib import Path
import sys

from yaml import safe_load
import xlsxwriter



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'target',
        type=Path,
        help='Path for Excel file')
    args = parser.parse_args()

    field_schemas = safe_load(
        (Path(__file__).parent.parent / 'docs/field-schemas.yaml').read_text()
    )

    all_schemas = set()
    for schemas in field_schemas.values():
        all_schemas |= set(schemas)
    
    schema_cols = list(all_schemas)

    workbook = xlsxwriter.Workbook(args.target)
    worksheet = workbook.add_worksheet()

    for row, field in enumerate(field_schemas):
        worksheet.write(row, 0, field)
        for col, schema in enumerate(schema_cols):
            if schema in field_schemas[field]:
                worksheet.write(row, col + 1, 'X')

    workbook.close()

if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
