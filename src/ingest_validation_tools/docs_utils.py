import re
from string import Template
from pathlib import Path


def get_tsv_name(type, is_assay=True):
    return f'{type}{"-metadata" if is_assay else ""}.tsv'


def get_xlsx_name(type, is_assay=True):
    return f'{type}{"-metadata" if is_assay else ""}.xlsx'


def generate_template_tsv(table_schema):
    names = [field['name'] for field in table_schema['fields']]
    header_row = '\t'.join(names)

    enums = [
        ' / '.join(str(e) for e in field['constraints']['enum'])
        if 'constraints' in field
        and 'enum' in field['constraints']
        else ''
        for field in table_schema['fields']
    ]
    enums_row = '\t'.join(enums)

    return '\n'.join([header_row, enums_row])


def _enrich_description(field):
    '''
    >>> good_field = {
    ...   'name': 'good-example',
    ...   'description': 'blah blah',
    ...   'constraints': {'required': False, 'pattern': r'[A-Z]+\\d+'},
    ...   'example': 'ABC123'
    ... }
    >>> _enrich_description(good_field)
    'blah blah. Leave blank if not applicable. Example: `ABC123`.'

    >>> bad_field = {
    ...   'name': 'bad-example',
    ...   'description': 'blah blah',
    ...   'constraints': {'pattern': r'[A-Z]+\\d+'},
    ...   'example': '123ABC'
    ... }
    >>> _enrich_description(bad_field)
    Traceback (most recent call last):
    ...
    Exception: bad-example's example (123ABC) does not match pattern ([A-Z]+\\d+)

    '''
    description = field['description'].strip()
    if description[-1] not in ['.', ')', '?']:
        description += '.'
    if 'required' in field:
        raise Exception('"required" should be in "constraints", not at top level')
    if (
        'constraints' in field
        and 'required' in field['constraints']
        and not field['constraints']['required']
    ):
        description += ' Leave blank if not applicable.'
    if 'example' in field:
        if 'constraints' not in field or 'pattern' not in field['constraints']:
            raise Exception(f'{field["name"]} has example but no pattern')
        if not re.match(field['constraints']['pattern'], field['example']):
            raise Exception(
                f"{field['name']}'s example ({field['example']}) "
                f"does not match pattern ({field['constraints']['pattern']})")
        description += f' Example: `{field["example"]}`.'
    return description.strip()


def generate_readme_md(
        table_schemas, directory_schema, schema_name, is_assay=True):
    max_version = max(table_schemas.keys())
    max_version_table_schema = table_schemas[max_version]

    raw_base_url = 'https://raw.githubusercontent.com/' \
        'hubmapconsortium/ingest-validation-tools/master/docs'

    src_url_base = 'https://github.com/hubmapconsortium' \
        '/ingest-validation-tools/edit/master/src/ingest_validation_tools'
    end_of_path = f'{"assays/" if is_assay else ""}{schema_name}.yaml'

    directory_source_url = f'{src_url_base}/directory-schemas/{schema_name}.yaml'
    optional_dir_schema_link_md, optional_dir_description_md = (
        (
            f'- [💻 Directory schema]({directory_source_url}): To update directory structure.',
            f'## Directory schema\n{_make_dir_description(directory_schema)}'
        ) if directory_schema else
        ('', '')
    )

    optional_doc_link_md = (
        f'- [🔬 Background doc]({max_version_table_schema["doc_url"]}): '
        'More details about this type.'
        if 'doc_url' in max_version_table_schema else ''
    )
    optional_description_md = (
        max_version_table_schema['description_md']
        if 'description_md' in max_version_table_schema else ''
    )

    template = Template(
        (Path(__file__).parent / 'docs.template').read_text()
    )
    return template.substitute({
        'schema_name': schema_name,
        'max_version': max_version,

        'tsv_url': f'{raw_base_url}/{schema_name}/{get_tsv_name(schema_name, is_assay=is_assay)}',
        'xlsx_url': f'{raw_base_url}/{schema_name}/{get_xlsx_name(schema_name, is_assay=is_assay)}',
        'metadata_source_url': f'{src_url_base}/table-schemas/{end_of_path}',

        'current_version_md':
            _make_fields_md(
                table_schemas[max_version], f'Version {max_version} (current)', is_open=True
            ),
        'previous_versions_md':
            '\n\n'.join([
                _make_fields_md(
                    table_schemas[str(v)], f'Version {v}'
                )
                for v in reversed(range(int(max_version)))
            ]),

        'optional_dir_schema_link_md': optional_dir_schema_link_md,
        'optional_dir_description_md': optional_dir_description_md,

        'optional_doc_link_md': optional_doc_link_md,
        'optional_description_md': optional_description_md
    })


def _make_fields_md(table_schema, title, is_open=False):
    fields_md_list = []
    for field in table_schema['fields']:
        if 'heading' in field:
            fields_md_list.append(f"### {field['heading']}")
        table_md = _make_constraints_table(field)
        fields_md_list.append('\n'.join([
            f"##### `{field['name']}`",
            _enrich_description(field),
            table_md
        ]))
    joined_list = '\n\n'.join(fields_md_list)
    return f'''
<details {'open="true"' if is_open else ''}><summary><b>{title}</b></summary>

{_make_toc(joined_list) if is_open else ''}
{joined_list}

</details>
'''


def _make_constraints_table(field):
    table_md_rows = ['| constraint | value |', '| --- | --- |']
    for key, value in field.items():
        if key in ['type', 'format']:
            if key == 'type' and value == 'string':
                continue
            table_md_rows.append(f'| {key} | `{value}` |')
    if 'constraints' in field:
        for key, value in field['constraints'].items():
            key_md = _make_key_md(key, value)
            value_md = _make_value_md(key, value)
            table_md_rows.append(f'| {key_md} | {value_md} |')
    if 'custom_constraints' in field:
        for key, value in field['custom_constraints'].items():
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
    other keys
    '''
    if key == 'pattern':
        return 'pattern (regular expression)'
    return key.replace('_', ' ')


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

    >>> print(_make_value_md('url', {'prefix': 'http://example.com/'}))
    prefix: `http://example.com/`

    '''
    if key == 'enum':
        backtick_list = [f'`{s}`' for s in value]
        if len(value) < 3:
            return ' or '.join(backtick_list)
        backtick_list[-1] = f'or {backtick_list[-1]}'
        return ', '.join(backtick_list)
    if key == 'pattern':
        return f'`{_md_escape_re(value)}`'
    if key == 'url':
        return f'prefix: `{_md_escape_re(value["prefix"])}`'
    return f'`{value}`'


def _md_escape_re(re_string):
    '''
    >>> print(_md_escape_re('a|b'))
    a\\|b
    '''
    return re.sub(r'([|])', r'\\\1', re_string)


def _make_toc(md):
    # Github should do this for us, but it doesn't.
    # Existing solutions expect a file, not a string,
    # or aren't Python at all, etc. Argh.
    # This is not good.
    '''
    >>> md = '# Section A\\n## `Item 1`\\n# Section B'

    >>> print(_make_toc(md))
    <blockquote><details><summary>Section A</summary>
    <BLANKLINE>
    [`Item 1`](#item-1)<br>
    </details>
    <BLANKLINE>
    <details><summary>Section B</summary>
    </details></blockquote>

    '''
    lines = md.split('\n')
    headers = [
        re.sub(r'^#+\s+', '', line)
        for line in lines if len(line) and line[0] == '#'
    ]
    mds = '\n'.join([
        (
            # Assume section headers do not contain backticks...
            f'</details>\n\n<details><summary>{h}</summary>\n'
            if '`' not in h else
            # Otherwise, make a link to the field:
            f"[{h}](#{h.lower().replace(' ', '-').replace('`', '')})<br>"
        )
        for h in headers
    ]).replace('</details>\n\n', '', 1) + '</details>'
    return f'<blockquote>{mds}</blockquote>'


def _make_dir_description(dir_schema):
    '''
    QA and Required flags are handled:

    >>> dir_schema = [
    ...   { 'pattern': 'required\\.txt', 'description': 'Required!',
    ...     'is_qa_qc': True },
    ...   { 'pattern': 'optional\\.txt', 'description': 'Optional!',
    ...     'required': False }
    ... ]
    >>> print(_make_dir_description(dir_schema))
    <BLANKLINE>
    | pattern | required? | description |
    | --- | --- | --- |
    | `required\\.txt` | ✓ | **[QA/QC]** Required! |
    | `optional\\.txt` |  | Optional! |

    Examples add an extra column:

    >>> dir_schema = [
    ...   { 'pattern': '[A-Z]+\\d+', 'description': 'letters numbers', 'example': 'ABC123'},
    ...   { 'pattern': '[A-Z]', 'description': 'one letter, no example'},
    ... ]
    >>> print(_make_dir_description(dir_schema))
    <BLANKLINE>
    | pattern | example | required? | description |
    | --- | --- | --- | --- |
    | `[A-Z]+\\d+` | `ABC123` | ✓ | letters numbers |
    | `[A-Z]` |  | ✓ | one letter, no example |

    Bad examples cause errors:

    >>> dir_schema = [
    ...   { 'pattern': '[A-Z]\\d', 'description': '1 letter 1 number', 'example': 'ABC123'},
    ... ]
    >>> _make_dir_description(dir_schema)
    Traceback (most recent call last):
    ...
    Exception: Example "ABC123" does not match pattern "[A-Z]\\d"

    '''
    has_examples = any('example' in line for line in dir_schema)

    output = []
    if has_examples:
        output.append('''
| pattern | example | required? | description |
| --- | --- | --- | --- |''')
    else:
        output.append('''
| pattern | required? | description |
| --- | --- | --- |''')

    for line in dir_schema:
        row = []

        pattern = line['pattern']
        pattern_md = f'`{_md_escape_re(pattern)}`'
        row.append(pattern_md)

        if has_examples:
            if 'example' not in line:
                row.append('')
            else:
                example = line['example']
                if not re.fullmatch(pattern, example):
                    raise Exception(f'Example "{example}" does not match pattern "{pattern}"')
                example_md = f'`{_md_escape_re(example)}`'
                row.append(example_md)

        required_md = '' if 'required' in line and not line['required'] else '✓'
        row.append(required_md)

        qa_qc_md = '**[QA/QC]** ' if 'is_qa_qc' in line and line['is_qa_qc'] else ''
        description_md = qa_qc_md + line['description']
        row.append(description_md)

        output.append('| ' + ' | '.join(row) + ' |')
    return '\n'.join(output)
