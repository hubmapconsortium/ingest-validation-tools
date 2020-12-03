#!/usr/bin/env python3

import argparse
from pathlib import Path
import sys

from tableschema_to_template.create_xlsx import create_xlsx

from ingest_validation_tools.schema_loader import (
    list_types, get_table_schema, get_other_schema, get_directory_schema)
from ingest_validation_tools.docs_utils import (
    get_tsv_name, get_xlsx_name,
    generate_template_tsv, generate_readme_md)
from ingest_validation_tools.argparse_types import dir_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'type',
        help='What type to generate')
    parser.add_argument(
        'target',
        type=dir_path,
        help='Directory to write output to')
    args = parser.parse_args()

    is_assay = args.type in list_types()
    if is_assay:
        table_schema = get_table_schema(args.type)
        directory_schema = get_directory_schema(args.type)
    else:
        table_schema = get_other_schema(args.type)
        directory_schema = {}

    # README:
    with open(Path(args.target) / 'README.md', 'w') as f:
        f.write(generate_readme_md(
            table_schema, directory_schema, args.type, is_top_level=(not is_assay)
        ))
        # TODO: Rename

    # Data entry templates:
    with open(Path(args.target) / get_tsv_name(args.type, is_assay=is_assay), 'w') as f:
        f.write(generate_template_tsv(table_schema))
    create_xlsx(table_schema, Path(args.target) / get_xlsx_name(args.type, is_assay=is_assay))


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
