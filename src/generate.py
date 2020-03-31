#!/usr/bin/env python

import argparse
from pathlib import Path
import sys
import re
import os

from yaml import safe_load as load_yaml, dump as dump_yaml


def _dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise Exception(f'"{string}" is not a directory')


def main():
    schemas_path = (
        Path(__file__).parent / 'hubmap_ingest_validator' / 'table-schemas'
    )
    valid_types = [p.stem for p in schemas_path.iterdir()]

    parser = argparse.ArgumentParser()
    parser.add_argument(
        'type',
        choices=valid_types,
        help='What type to generate')
    parser.add_argument(
        'target',
        type=_dir_path,
        help='Directory to write output to')
    args = parser.parse_args()

    schema_path = schemas_path / f'{args.type}.yaml'
    table_schema = load_yaml(open(schema_path).read())

    with open(Path(args.target) / 'template.tsv', 'w') as f:
        f.write(_generate_template_tsv(table_schema))
    with open(Path(args.target) / 'schema.yaml', 'w') as f:
        f.write(_generate_schema_yaml(table_schema))
    with open(Path(args.target) / 'README.md', 'w') as f:
        f.write(_generate_readme_md(table_schema, args.type))


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
        table_md_rows = ['| constraint | value |', '| --- | --- |']
        for key, value in field.items():
            if key in ['type', 'format']:
                table_md_rows.append(f'| {key} | `{value}` |')
        if 'constraints' in field:
            for key, value in field['constraints'].items():
                table_md_rows.append(f'| {key} | `{value}` |')
        if len(table_md_rows) < 3:
            # Empty it, if there is no data.
            table_md_rows = []
        table_md = '\n'.join(table_md_rows)
        fields_md_list.append(
            f"### `{field['name']}`\n{field['description']}\n\n{table_md}"
        )

    fields_md = '\n\n'.join(fields_md_list)
    toc_md = _make_toc(fields_md)
    raw_url = 'https://raw.githubusercontent.com/hubmapconsortium' + \
        f'/ingest-validation-tools/master/docs/{type}/template.tsv'

    return f'''# {type}

Related files:
- [JSON Schema](schema.yaml)
- [TSV Template]({raw_url})

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
