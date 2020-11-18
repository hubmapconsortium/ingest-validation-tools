#!/usr/bin/env python3

import argparse
from pathlib import Path
import sys

from ingest_validation_tools.docs_utils import (
    get_tsv_name, generate_template_tsv, generate_readme_md)
from ingest_validation_tools.schema_loader import (
    get_other_schema)
from ingest_validation_tools.argparse_types import dir_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'type',
        type=str,
        help='Type to generate')
    parser.add_argument(
        'target',
        type=dir_path,
        help='Directory to write output to')
    args = parser.parse_args()

    table_schema = get_other_schema(args.type)

    (Path(args.target) / get_tsv_name(args.type)).write_text(
        generate_template_tsv(
            table_schema))
    (Path(args.target) / 'README.md').write_text(
        generate_readme_md(
            table_schema, {}, args.type, is_top_level=True))


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
