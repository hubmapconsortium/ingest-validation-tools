#!/usr/bin/env python3

import argparse
from pathlib import Path
import sys
from datetime import datetime

from yaml import safe_load
import xlsxwriter


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'target',
        type=Path,
        help='Path for Excel file')
    args = parser.parse_args()

    docs_path = Path(__file__).parent.parent / 'docs'
    field_schemas = safe_load((docs_path / 'field-schemas.yaml').read_text())
    field_descriptions = safe_load((docs_path / 'field-descriptions.yaml').read_text())

    all_schemas = set()
    for schemas in field_schemas.values():
        all_schemas |= set(schemas)

    schema_cols = sorted(all_schemas)

    workbook = xlsxwriter.Workbook(args.target)
    worksheet = workbook.add_worksheet('schemas + fields')
    workbook.set_properties({
        # So regenerated Excel files will be binary identical:
        'created': datetime(2000, 1, 1)
    })

    # Set column widths:
    worksheet.set_column(0, 0, 40)
    worksheet.set_column(1, len(schema_cols), 2)

    # Format and write headers:
    header_format = workbook.add_format({'rotation': 60})
    worksheet.freeze_panes(1, 1)
    for col, schema in enumerate(schema_cols):
        worksheet.write(0, col + 1, schema, header_format)

    # Write body of grid:
    for row, field in enumerate(field_schemas):
        worksheet.write(row + 1, 0, field)
        worksheet.write_comment(row + 1, 0, field_descriptions[field])
        for col, schema in enumerate(schema_cols):
            if schema in field_schemas[field]:
                worksheet.write(row + 1, col + 1, '✓')

    workbook.close()


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
