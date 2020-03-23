#!/usr/bin/env python

import argparse
from pathlib import Path
import sys
import re

from yaml import safe_load as load_yaml, dump as dump_yaml


def main():
    schemas_path = (
        Path(__file__).parent / 'hubmap_ingest_validator' / 'table-schemas'
    )
    valid_types = [p.stem for p in schemas_path.iterdir()]

    parser = argparse.ArgumentParser()
    parser.add_argument(
        'type',
        choices=valid_types,
        help='What type to generate for')
    parser.add_argument(
        'target',
        choices=['template.tsv', 'schema.yaml', 'README.md'],
        help='What kind of thing to generate')
    args = parser.parse_args()

    schema_path = schemas_path / f'{args.type}.yaml'
    table_schema = load_yaml(open(schema_path).read())

    if args.target == 'template.tsv':
        print(_generate_template_tsv(table_schema))
    elif args.target == 'schema.yaml':
        print(_generate_schema_yaml(table_schema))
    elif args.target == 'README.md':
        print(_generate_readme_md(table_schema, args.type))


def _generate_template_tsv(table_schema):
    names = [field['name'] for field in table_schema['fields']]
    return '\t'.join(names) + '\n'


def _generate_schema_yaml(table_schema):
    json_schema = {
        'properties': {
            field['name']: {
                'type': 'string',  # TODO: for now...
                'description': field['description']
            } for field in table_schema['fields']
        }
    }
    return dump_yaml(json_schema)


def _generate_readme_md(table_schema, type):
    fields_md_list = []
    for field in table_schema['fields']:
        if 'heading' in field:
            fields_md_list.append(f"## {field['heading']}")
        table_md_rows = ['| --- | --- |']
        for key, value in field.items():
            if key not in ['heading', 'name', 'description']:
                table_md_rows.append(f'| {key} | `{value}` |')
        if len(table_md_rows) == 1:
            # Empty it, if there is no data.
            table_md_rows = []
        table_md = '\n'.join(table_md_rows)
        fields_md_list.append(
            f"### `{field['name']}`\n{field['description']}\n{table_md}"
        )

    fields_md = '\n\n'.join(fields_md_list)
    toc_md = _make_toc(fields_md)

    return f'''# {type}

Related files:
- [JSON Schema](schema.yaml)
- [TSV Template](template.tsv)

## Table of contents
{toc_md}

{fields_md}
'''


def _make_toc(md):
    # Github should do this for us, but it doesn't.
    # Existing solutions expect a file, not a string,
    # or aren't Python at all, etc. Argh.
    # This is not good.
    lines = md.split('\n')
    headers = [
        re.sub(r'^#+\s+', '', l)
        for l in lines if len(l) and l[0] == '#'
    ]
    return '\n'.join([
        f"[{h}](#{h.lower().replace(' ', '-').replace('`', '')})<br>"
        for h in headers
    ])


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
