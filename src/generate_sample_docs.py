#!/usr/bin/env python3

import argparse
from pathlib import Path
import sys

from yaml import safe_load as load_yaml

from ingest_validation_tools.docs_utils import (
    get_tsv_name, generate_template_tsv, generate_readme_md
)
from ingest_validation_tools.argparse_types import dir_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'target',
        type=dir_path,
        help='Directory to write output to')
    args = parser.parse_args()

    metadata_type = 'sample'

    table_schema = load_yaml(
        (Path(__file__).parent / 'ingest_validation_tools' / 'table-schemas' /
         'sample.yaml').read_text()
    )

    with open(Path(args.target) / get_tsv_name(metadata_type), 'w') as f:
        f.write(generate_template_tsv(table_schema))
    with open(Path(args.target) / 'README.md', 'w') as f:
        f.write(generate_readme_md(
            table_schema, metadata_type, is_top_level=True))


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
