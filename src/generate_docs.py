#!/usr/bin/env python3

import argparse
from pathlib import Path
import sys
import re
import os

from yaml import dump as dump_yaml

from ingest_validation_tools.table_schema_loader import list_types, get_schema


def _dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise Exception(f'"{string}" is not a directory')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'type',
        choices=list_types(),
        help='What type to generate')
    parser.add_argument(
        'target',
        type=_dir_path,
        help='Directory to write output to')
    args = parser.parse_args()

    table_schema = get_schema(args.type)

    with open(Path(args.target) / 'template.tsv', 'w') as f:
        f.write(_generate_template_tsv(table_schema))
    # The generated JSON Schema is easy to confuse with
    # the source Table Schema. Until we know it's definitely
    # needed, stop producing it.
    #
    # with open(Path(args.target) / 'schema.yaml', 'w') as f:
    #     f.write(_generate_json_schema_yaml(table_schema))
    with open(Path(args.target) / 'README.md', 'w') as f:
        f.write(_generate_readme_md(table_schema, args.type))


def _generate_template_tsv(table_schema):
    names = [field['name'] for field in table_schema['fields']]
    return '\t'.join(names) + '\n'


def _generate_json_schema_yaml(table_schema):
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
        table_md = _make_constraints_table(field)
        fields_md_list.append(
            f"### `{field['name']}`\n{field['description']}\n\n{table_md}"
        )

    fields_md = '\n\n'.join(fields_md_list)
    toc_md = _make_toc(fields_md)
    raw_url = 'https://raw.githubusercontent.com/hubmapconsortium' + \
        f'/ingest-validation-tools/master/docs/{type}/template.tsv'
    source_url = 'https://github.com/hubmapconsortium' + \
        '/ingest-validation-tools/edit/master' + \
        f'/src/ingest_validation_tools/table-schemas/{type}.yaml'

    return f'''# {type}

Related files:
- [🔬 Background doc]({table_schema['doc_url']}): More details about this type.
- [📝 TSV template]({raw_url}): Use this to submit metadata.
- [💻 Source code]({source_url}): Make a PR if this doc should be updated.

## Table of contents
{toc_md}

{fields_md}
'''


def _make_constraints_table(field):
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
    return '\n'.join(table_md_rows)


def _make_toc(md):
    # Github should do this for us, but it doesn't.
    # Existing solutions expect a file, not a string,
    # or aren't Python at all, etc. Argh.
    # This is not good.
    '''
    >>> md = '# Section A\\n## `Item 1`\\n# Section B'

    >>> print(_make_toc(md))
    <details><summary>Section A</summary>
    <BLANKLINE>
    [`Item 1`](#item-1)<br>
    </details>
    <BLANKLINE>
    <details><summary>Section B</summary>
    </details>

    '''
    lines = md.split('\n')
    headers = [
        re.sub(r'^#+\s+', '', l)
        for l in lines if len(l) and l[0] == '#'
    ]
    return '\n'.join([
        (
            # Assume section headers do not contain backticks...
            f'</details>\n\n<details><summary>{h}</summary>\n'
            if '`' not in h else
            # Otherwise, make a link to the field:
            f"[{h}](#{h.lower().replace(' ', '-').replace('`', '')})<br>"
        )
        for h in headers
    ]).replace('</details>\n\n', '', 1) + '</details>'


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
