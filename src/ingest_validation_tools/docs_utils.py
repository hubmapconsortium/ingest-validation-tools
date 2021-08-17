import re
from string import Template
from pathlib import Path

from ingest_validation_tools.schema_loader import get_field_enum


def get_tsv_name(type, is_assay=True):
    return f'{type}{"-metadata" if is_assay else ""}.tsv'


def get_xlsx_name(type, is_assay=True):
    return f'{type}{"-metadata" if is_assay else ""}.xlsx'


def generate_template_tsv(table_schema):
    '''
    >>> schema = {'fields': [{
    ...   'name': 'fake',
    ...   'constraints': {
    ...     'enum': ['a', 'b', 'c']
    ...   }
    ... }]}
    >>> generate_template_tsv(schema)
    'fake\\na / b / c'
    '''

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
        table_schemas, pipeline_infos, directory_schemas, schema_name, is_assay=True):
    int_keys = [int(k) for k in table_schemas.keys()]
    max_version = max(int_keys)
    min_version = min(int_keys)
    max_version_table_schema = table_schemas[str(max_version)]

    assay_type_enum = get_field_enum('assay_type', max_version_table_schema)
    assay_category_enum = get_field_enum('assay_category', max_version_table_schema)
    source_project_enum = get_field_enum('source_project', max_version_table_schema)

    title = ' / '.join(assay_type_enum) \
        if assay_type_enum else schema_name
    category = ' / '.join(assay_category_enum) \
        if assay_category_enum else 'other'
    title += f" ({' / '.join(source_project_enum)})" \
        if source_project_enum else ''

    raw_base_url = 'https://raw.githubusercontent.com/' \
        'hubmapconsortium/ingest-validation-tools/main/docs'

    optional_dir_description_md = (
        f'## Directory schemas\n{_make_dir_descriptions(directory_schemas, pipeline_infos)}'
        if directory_schemas else ''
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
        'title': title,
        'schema_name': schema_name,
        'category': {
            'imaging': 'Imaging assays',
            'mass_spectrometry': 'Mass spectrometry',
            'mass_spectrometry_imaging': 'Imaging mass spectrometry',
            'sequence': 'Sequence assays',
            'other': 'Other TSVs'
        }[category],
        'max_version': max_version,
        'all_versions_deprecated':
            all(schema.get('deprecated') for schema in table_schemas.values()),

        'tsv_url': f'{raw_base_url}/{schema_name}/{get_tsv_name(schema_name, is_assay=is_assay)}',
        'xlsx_url': f'{raw_base_url}/{schema_name}/{get_xlsx_name(schema_name, is_assay=is_assay)}',

        'current_version_md':
            _make_fields_md(
                max_version_table_schema, f'Version {max_version} (current)', is_open=True
        ),
        'previous_versions_md':
            '\n\n'.join([
                _make_fields_md(table_schemas[str(v)], f'Version {v}')
                for v in range(max_version - 1, min_version - 1, -1)
            ]),

        'optional_dir_description_md': optional_dir_description_md,

        'optional_doc_link_md': optional_doc_link_md,
        'optional_description_md': optional_description_md
    })


def _make_fields_md(table_schema, title, is_open=False):
    '''
    >>> schema = {'fields': [{
    ...   'heading': 'A head',
    ...   'name': 'a_name',
    ...   'description': 'A description'
    ... }]}
    >>> print(_clean(_make_fields_md(schema, 'A title')))
    <details markdown="1" ><summary><b>A title</b></summary>
    ### A head
    <a name="a_name"></a>
    ##### [`a_name`](#a_name)
    A description.
    </details>

    >>> schema = {'deprecated': True, 'fields': []}
    >>> print(_clean(_make_fields_md(schema, 'A title', is_open=True)))
    <details markdown="1" open="true"><summary><s>A title</s> (deprecated)</summary>
    <blockquote markdown="1">
    </blockquote>
    </details>
    '''

    fields_md_list = []
    for field in table_schema['fields']:
        if 'heading' in field:
            fields_md_list.append(f"### {field['heading']}")
        table_md = _make_constraints_table(field)
        name = field['name']
        fields_md_list.append('\n'.join([
            f'<a name="{name}"></a>',
            f"##### [`{name}`](#{name})",
            _enrich_description(field),
            table_md
        ]))
    joined_list = '\n\n'.join(fields_md_list)
    if table_schema.get('deprecated'):
        title_html = f'<s>{title}</s> (deprecated)'
    else:
        title_html = f'<b>{title}</b>'
    return f'''
<details markdown="1" {'open="true"' if is_open else ''}><summary>{title_html}</summary>

{_make_toc(joined_list) if is_open else ''}
{joined_list}

</details>
'''


def _make_constraints_table(field):
    '''
    >>> field = {
    ...   'name': 'field',
    ...   'type': 'fake type',
    ...   'constraints': {
    ...     'enum': ['a', 'b']
    ...   },
    ...   'custom_constraints': {
    ...     'custom': 'fake',
    ...   }
    ... }
    >>> print(_make_constraints_table(field))
    <BLANKLINE>
    | constraint | value |
    | --- | --- |
    | type | `fake type` |
    | enum | `a` or `b` |
    | custom | `fake` |
    '''

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
            if key in ['sequence_limit', 'forbid_na']:
                # Applied to every field,
                # but we don't want to clutter the docs:
                continue
            key_md = _make_key_md(key, value)
            value_md = _make_value_md(key, value)
            table_md_rows.append(f'| {key_md} | {value_md} |')
    if len(table_md_rows) < 3:
        # Empty it, if there is no data.
        table_md_rows = []
    main_table_md = '\n'.join(table_md_rows)

    ontology_table_md = _make_ontology_table(field['constraints']['enum']) \
        if 'constraints' in field and 'enum' in field['constraints'] else ''
    return '\n' + main_table_md + ontology_table_md


def _make_ontology_table(enum):
    if not isinstance(enum, dict):
        return ''
    table_md_rows = ['| term | URI |', '| --- | --- |']
    for term, uri in enum.items():
        table_md_rows.append(f'| {term} | `{uri}` |')
    return '\n\nOntology terms:\n\n' + '\n'.join(table_md_rows)


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


def _clean(s):
    return re.sub(r'\n+', '\n', s).strip()


def _make_toc(md):
    # Github should do this for us, but it doesn't.
    # Existing solutions expect a file, not a string,
    # or aren't Python at all, etc. Argh.
    # This is not good.
    '''
    >>> md = '# Section A\\n## `Item 1`\\n# Section B'

    >>> print(_clean(_make_toc(md)))
    <blockquote markdown="1">
    <details markdown="1"><summary>Section A</summary>
    [`Item 1`](#item-1)<br>
    </details>
    <details markdown="1"><summary>Section B</summary>
    </details>
    </blockquote>

    >>> md = '## `Item 1`\\n## `Item 3`\\n## `Item 3`\\n'

    >>> print(_clean(_make_toc(md)))
    <blockquote markdown="1">
    [`Item 1`](#item-1)<br>
    [`Item 3`](#item-3)<br>
    [`Item 3`](#item-3)<br>
    </blockquote>

    '''
    lines = md.split('\n')
    headers = [
        re.sub(r'^#+\s*', '', re.sub(r'.*\[(.*)\].*', r'\1', line))
        for line in lines if len(line) and line[0] == '#'
    ]
    in_details = False
    mds = []
    for h in headers:
        if '`' in h:
            mds.append(f"[{h}](#{h.lower().replace(' ', '-').replace('`', '')})<br>")
        else:
            if in_details:
                mds.append('\n</details>')
            mds.append(f'<details markdown="1"><summary>{h}</summary>\n')
            in_details = True
    if in_details:
        mds.append('</details>')
    joined_mds = "\n".join(mds)
    # If MD trails immediately after "</blockquote>",
    # it doesn't render correctly, so include a newline.
    return f'<blockquote markdown="1">\n\n{joined_mds}\n\n</blockquote>\n'


def _make_dir_descriptions(dir_schemas, pipeline_infos):
    '''
    >>> dir_schema = [
    ...   { 'pattern': 'required\\.txt', 'description': 'Required!'}
    ... ]
    >>> pipeline_infos = [{
    ...     "name": "Fake Pipeline",
    ...     "repo_url": "https://github.com/hubmapconsortium/fake",
    ...     "version_tag": "v1.2.3"
    ... }]
    '''
    pipeline_infos_md = ' and '.join(make_pipeline_link(info) for info in pipeline_infos)
    pipeline_blurb = \
        f'The HIVE will process each dataset with\n{pipeline_infos_md}.\n' \
        if pipeline_infos else ''

    sorted_items = sorted(dir_schemas.items(), key=lambda item: item[0], reverse=True)
    return pipeline_blurb + '\n'.join(
        f'### v{v}\n' + _make_dir_description(schema['files'], schema.get('deprecated', False))
        for v, schema in sorted_items
    )


def _make_dir_description(files, is_deprecated=False):
    '''
    QA and Required flags are handled:

    >>> files = [
    ...   { 'pattern': 'required\\.txt', 'description': 'Required!',
    ...     'is_qa_qc': True },
    ...   { 'pattern': 'optional\\.txt', 'description': 'Optional!',
    ...     'required': False }
    ... ]
    >>> print(_make_dir_description(files))
    <BLANKLINE>
    | pattern | required? | description |
    | --- | --- | --- |
    | `required\\.txt` | ✓ | **[QA/QC]** Required! |
    | `optional\\.txt` |  | Optional! |

    Deprecated is handled:

    >>> files = [
    ...   { 'pattern': 'optional\\.txt', 'description': 'Optional!',
    ...     'required': False }
    ... ]
    >>> print(_make_dir_description(files, True))
    <details markdown="1"><summary>Deprecated</summary>
    <BLANKLINE>
    | pattern | required? | description |
    | --- | --- | --- |
    | `optional\\.txt` |  | Optional! |
    <BLANKLINE>
    </details>

    Examples add an extra column:

    >>> files = [
    ...   { 'pattern': '[A-Z]+\\d+', 'description': 'letters numbers', 'example': 'ABC123'},
    ...   { 'pattern': '[A-Z]', 'description': 'one letter, no example'},
    ... ]
    >>> print(_make_dir_description(files))
    <BLANKLINE>
    | pattern | example | required? | description |
    | --- | --- | --- | --- |
    | `[A-Z]+\\d+` | `ABC123` | ✓ | letters numbers |
    | `[A-Z]` |  | ✓ | one letter, no example |

    Bad examples cause errors:

    >>> files = [
    ...   { 'pattern': '[A-Z]\\d', 'description': '1 letter 1 number', 'example': 'ABC123'},
    ... ]
    >>> _make_dir_description(files)
    Traceback (most recent call last):
    ...
    AssertionError: Example "ABC123" does not match pattern "[A-Z]\\d"

    Unexpected flags cause error:

    >>> files = [
    ...   { 'bad': 'schema' }
    ... ]
    >>> _make_dir_description(files)
    Traceback (most recent call last):
    ...
    AssertionError: Unexpected key "bad" in {'bad': 'schema'}
    '''
    for line in files:
        for k in line.keys():
            assert k in {'pattern', 'required', 'description', 'example', 'is_qa_qc'}, \
                f'Unexpected key "{k}" in {line}'

    has_examples = any('example' in line for line in files)

    output = []
    if has_examples:
        output.append('''
| pattern | example | required? | description |
| --- | --- | --- | --- |''')
    else:
        output.append('''
| pattern | required? | description |
| --- | --- | --- |''')

    for line in files:
        row = []

        pattern = line['pattern']
        pattern_md = f'`{_md_escape_re(pattern)}`'
        row.append(pattern_md)

        if has_examples:
            if 'example' not in line:
                row.append('')
            else:
                example = line['example']
                assert re.fullmatch(pattern, example), \
                    f'Example "{example}" does not match pattern "{pattern}"'
                example_md = f'`{_md_escape_re(example)}`'
                row.append(example_md)

        required_md = '' if 'required' in line and not line['required'] else '✓'
        row.append(required_md)

        qa_qc_md = '**[QA/QC]** ' if 'is_qa_qc' in line and line['is_qa_qc'] else ''
        description_md = qa_qc_md + line['description']
        row.append(description_md)

        output.append('| ' + ' | '.join(row) + ' |')
    table = '\n'.join(output)

    if is_deprecated:
        return f'<details markdown="1"><summary>Deprecated</summary>\n{table}\n\n</details>'
    return table


def make_pipeline_link(info):
    '''
    >>> info = {
    ...     "name": "Fake Pipeline",
    ...     "repo_url": "https://github.com/hubmapconsortium/fake",
    ...     "version_tag": "v1.2.3"
    ... }
    >>> print(make_pipeline_link(info))
    [Fake Pipeline v1.2.3](https://github.com/hubmapconsortium/fake/releases/tag/v1.2.3)
    '''
    text = f"{info['name']} {info['version_tag']}"
    href = f"{info['repo_url']}/releases/tag/{info['version_tag']}"
    return f"[{text}]({href})"
