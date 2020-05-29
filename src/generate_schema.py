#!/usr/bin/env python3

import csv
import sys
import argparse

from yaml import dump as dump_yaml


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--fields',
        type=argparse.FileType('r'),
        help='Two-column TSV: Field name and description')
    args = parser.parse_args()

    field_list = []
    for row in csv.reader(args.fields, dialect='excel-tab'):
        if len(row) == 2:
            field_list.append({
                'name': row[0],
                'description': row[1]
            })
    field_list[0] = {
        # Rebuild dict, so 'heading' is first.
        'heading': 'Level 2',
        **field_list[0]
    }
    level_1_overrides = [
        {
            'name': name,
            'constraints': {
                'enum': ['TODO']
            }
        }
        for name in ['assay_category', 'assay_type', 'analyte_class']
    ]
    print(dump_yaml({
        'doc_url': 'TODO',
        'fields': level_1_overrides + field_list
    }, sort_keys=False))

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
