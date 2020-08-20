import re


def get_tsv_name(type):
    return f'{type}-metadata.tsv'


def generate_template_tsv(table_schema):
    names = [field['name'] for field in table_schema['fields']]
    header_row = '\t'.join(names)

    enums = [
        ' / '.join(field['constraints']['enum'])
        if 'constraints' in field
        and 'enum' in field['constraints']
        else ''
        for field in table_schema['fields']
    ]
    enums_row = '\t'.join(enums)

    return '\n'.join([header_row, enums_row])


def _enrich_description(field):
    '''
    >>> field = {
    ...   'description': 'something',
    ...   'constraints': {'required': False}
    ... }
    >>> _enrich_description(field)
    'something. Leave blank if not applicable.'

    '''
    if (
        'constraints' in field
        and 'required' in field['constraints']
        and not field['constraints']['required']
    ):
        stripped = re.sub(r'\W+\s*$', '', field['description'])
        return stripped + '. Leave blank if not applicable.'
    return field['description']


def generate_readme_md(
        table_schema, directory_schema, type, is_top_level=False):
    fields_md_list = []
    for field in table_schema['fields']:
        if 'heading' in field:
            fields_md_list.append(f"## {field['heading']}")
        table_md = _make_constraints_table(field)
        fields_md_list.append(f"""### `{field['name']}`
{_enrich_description(field)}

{table_md}""")

    fields_md = '\n\n'.join(fields_md_list)
    toc_md = _make_toc(fields_md)
    dir_description_md = _make_dir_description(directory_schema)
    raw_url = 'https://raw.githubusercontent.com/hubmapconsortium' \
        '/ingest-validation-tools/master/docs' \
        f'/{type}/{get_tsv_name(type)}'
    end_of_path = f'{"" if is_top_level else "level-2/"}{type}.yaml'
    source_url = 'https://github.com/hubmapconsortium' \
        '/ingest-validation-tools/edit/master' \
        f'/src/ingest_validation_tools/table-schemas/{end_of_path}'

    return f'''# {type}

Related files:
- [🔬 Background doc]({table_schema['doc_url']}): More details about this type.
- [📝 TSV template]({raw_url}): Use this to submit metadata.
- [💻 Source code]({source_url}): Make a PR if this doc should be updated.

## Table of contents
{toc_md}

## Directory description
{dir_description_md}

{fields_md}
'''


def _make_constraints_table(field):
    table_md_rows = ['| constraint | value |', '| --- | --- |']
    for key, value in field.items():
        if key in ['type', 'format']:
            table_md_rows.append(f'| {key} | `{value}` |')
    if 'constraints' in field:
        for key, value in field['constraints'].items():
            key_md = _make_key_md(key, value)
            value_md = _make_value_md(key, value)
            table_md_rows.append(f'| {key_md} | {value_md} |')
    if len(table_md_rows) < 3:
        # Empty it, if there is no data.
        table_md_rows = []
    return '\n'.join(table_md_rows)


def _make_key_md(key, value):
    '''
    >>> print(_make_key_md('pattern', 'some_reg_ex'))
    pattern (regular expression)

    >>> print(_make_key_md('other_keys', 'other_values'))
    other_keys
    '''
    if key == 'pattern':
        return 'pattern (regular expression)'
    return key


def _make_value_md(key, value):
    '''
    >>> print(_make_value_md('not_enum', 'abc'))
    `abc`

    >>> print(_make_value_md('enum', ['A']))
    `A`

    >>> print(_make_value_md('enum', ['A', 'B']))
    `A` or `B`

    >>> print(_make_value_md('enum', ['A', 'B', 'C']))
    `A`, `B`, or `C`

    >>> print(_make_value_md('pattern', '^some|reg_?ex\\.$'))
    `^some\\|reg_?ex\\.$`
    '''
    if key == 'enum':
        backtick_list = [f'`{s}`' for s in value]
        if len(value) < 3:
            return ' or '.join(backtick_list)
        backtick_list[-1] = f'or {backtick_list[-1]}'
        return ', '.join(backtick_list)
    if key == 'pattern':
        return '`' + re.sub(r'([|])', r'\\\1', value) + '`'
    return f'`{value}`'


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


def _make_dir_description(dir_schema):
    return f"""
'''
{dir_schema}
'''
"""
