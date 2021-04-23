#!/usr/bin/env python3

import argparse
from pathlib import Path
import sys
from yaml import dump as dump_yaml

from tableschema_to_template.create_xlsx import create_xlsx

from ingest_validation_tools.schema_loader import (
    dict_schema_versions, get_table_schema, get_other_schema, get_directory_schema,
    get_is_assay)
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

    schema_versions = dict_schema_versions()
    versions = sorted(schema_versions[args.type])
    max_version = max(versions)

    is_assay = get_is_assay(args.type)
    if is_assay:
        table_schemas = {v: get_table_schema(args.type, v) for v in versions}
        directory_schema = get_directory_schema(args.type)
    else:
        table_schemas = {v: get_other_schema(args.type, v) for v in versions}
        directory_schema = {}

    # README.md:
    with open(Path(args.target) / 'README.md', 'w') as f:
        f.write('Moved to [index.md]. (Move to github pages is in process.)')

    # index.md:
    with open(Path(args.target) / 'index.md', 'w') as f:
        f.write(generate_readme_md(
            table_schemas, directory_schema, args.type, is_assay=is_assay
        ))

    # YAML:
    for v in versions:
        with open(Path(args.target) / f'v{v}.yaml', 'w') as f:
            f.write(
                '# Generated YAML: PRs should not start here!\n'
                + dump_yaml(table_schemas[v])
            )

    # Data entry templates:
    with open(Path(args.target) / get_tsv_name(args.type, is_assay=is_assay), 'w') as f:
        max_schema = table_schemas[max_version]
        f.write(generate_template_tsv(max_schema))
    create_xlsx(
        max_schema, Path(args.target) / get_xlsx_name(args.type, is_assay=is_assay),
        idempotent=True,
        sheet_name='Export as TSV'
    )


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
