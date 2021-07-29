#!/usr/bin/env python3

import argparse
from pathlib import Path
import sys
from yaml import dump as dump_yaml

from tableschema_to_template.create_xlsx import create_xlsx

from ingest_validation_tools.schema_loader import (
    dict_table_schema_versions, get_table_schema, get_other_schema,
    dict_directory_schema_versions, get_directory_schema,
    get_is_assay, enum_maps_to_lists)
from ingest_validation_tools.docs_utils import (
    get_tsv_name, get_xlsx_name,
    generate_template_tsv, generate_readme_md)
from ingest_validation_tools.cli_utils import dir_path


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

    table_schema_versions = sorted(dict_table_schema_versions()[args.type])
    assert table_schema_versions, f'No versions for {args.type}'
    max_version = max(table_schema_versions)

    is_assay = get_is_assay(args.type)
    if is_assay:
        table_schemas = {v: get_table_schema(args.type, v) for v in table_schema_versions}
        directory_schema_versions = sorted(dict_directory_schema_versions()[args.type])
        directory_schemas = {
            v: get_directory_schema(args.type, v)['files']
            for v in directory_schema_versions
        }
    else:
        table_schemas = {v: get_other_schema(args.type, v) for v in table_schema_versions}
        directory_schemas = []

    # README.md:
    with open(Path(args.target) / 'README.md', 'w') as f:
        url = f'https://hubmapconsortium.github.io/ingest-validation-tools/{args.type}/'
        f.write(f'Moved to [github pages]({url}).')

    # index.md:
    with open(Path(args.target) / 'index.md', 'w') as f:
        f.write(generate_readme_md(
            table_schemas, directory_schemas, args.type, is_assay=is_assay
        ))

    # YAML:
    for v in table_schema_versions:
        schema = table_schemas[v]
        first_field = schema['fields'][0]
        if first_field['name'] == 'version':
            assert first_field['constraints']['enum'] == [v], \
                f'Wrong version constraint in {args.type}-v{v}.yaml'
        assert schema['fields'][0]
        with open(Path(args.target) / f'v{v}.yaml', 'w') as f:
            f.write(
                '# Generated YAML: PRs should not start here!\n'
                + dump_yaml(schema)
            )

    # Data entry templates:
    with open(Path(args.target) / get_tsv_name(args.type, is_assay=is_assay), 'w') as f:
        max_schema = enum_maps_to_lists(table_schemas[max_version],
                                        add_none_of_the_above=True, add_suggested=True)
        f.write(generate_template_tsv(max_schema))
    create_xlsx(
        max_schema, Path(args.target) / get_xlsx_name(args.type, is_assay=is_assay),
        idempotent=True,
        sheet_name='Export as TSV'
    )


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
