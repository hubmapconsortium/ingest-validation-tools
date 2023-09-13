import re
from string import Template
from pathlib import Path
import html
from typing import Dict, Any
from urllib.parse import urlencode

import requests

from ingest_validation_tools.schema_loader import get_field_enum, get_fields_wo_headers


def get_tsv_name(type: str, is_assay: bool = True) -> str:
    return f'{type}{"-metadata" if is_assay else ""}.tsv'


def get_xlsx_name(type: str, is_assay: bool = True) -> str:
    return f'{type}{"-metadata" if is_assay else ""}.xlsx'


def generate_template_tsv(table_schema: Dict) -> str:
    """
    >>> schema = {'fields': [{
    ...   'name': 'fake',
    ...   'constraints': {
    ...     'enum': ['a', 'b', 'c']
    ...   }
    ... }]}
    >>> generate_template_tsv(schema)
    'fake\\na / b / c'
    """

    names = [field["name"] for field in get_fields_wo_headers(table_schema)]
    header_row = "\t".join(names)

    enums = [
        " / ".join(str(e) for e in field["constraints"]["enum"])
        if "constraints" in field and "enum" in field["constraints"]
        else ""
        for field in table_schema["fields"]
    ]
    enums_row = "\t".join(enums)

    return "\n".join([header_row, enums_row])


def _enrich_description(field: Dict[str, Any]) -> str:
    """
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

    """
    description = field["description"].strip()
    if description[-1] not in [".", ")", "?"]:
        description += "."
    if "required" in field:
        raise Exception('"required" should be in "constraints", not at top level')
    if (
        "constraints" in field
        and "required" in field["constraints"]
        and not field["constraints"]["required"]
    ):
        description += " Leave blank if not applicable."
    if "example" in field:
        if "constraints" not in field or "pattern" not in field["constraints"]:
            raise Exception(f'{field["name"]} has example but no pattern')
        if not re.match(field["constraints"]["pattern"], field["example"]):
            raise Exception(
                f"{field['name']}'s example ({field['example']}) "
                f"does not match pattern ({field['constraints']['pattern']})"
            )
        description += f' Example: `{field["example"]}`.'
    return description.strip()


def _get_portal_name(assay_type):
    response = requests.post(
        "https://search.api.hubmapconsortium.org/assayname",
        json={"name": assay_type},
        headers={"Content-Type": "application/json"},
    ).json()
    try:
        return response["description"]
    except KeyError:
        return None


def _get_portal_names_md(assay_types):
    links = []
    for assay_type in assay_types:
        portal_name = _get_portal_name(assay_type)
        if portal_name is None:
            links.append(f"{assay_type} not in Portal")
            continue
        query = urlencode(
            {"mapped_data_types[0]": portal_name, "entity_type[0]": "Dataset"}
        )
        url = f"https://portal.hubmapconsortium.org/search?{query}"
        links.append(f"[{portal_name}]({url})")
    return f'In the portal: {" / ".join(links)}'


def generate_readme_md(
    table_schemas, pipeline_infos, directory_schemas, schema_name, is_assay=True
):
    int_keys = [int(k) for k in table_schemas.keys()]
    max_version = max(int_keys)
    min_version = min(int_keys)
    max_version_table_schema = table_schemas[str(max_version)]

    assay_type_enum = get_field_enum("assay_type", max_version_table_schema)
    assay_category_enum = get_field_enum("assay_category", max_version_table_schema)
    source_project_enum = get_field_enum("source_project", max_version_table_schema)

    title = " / ".join(assay_type_enum) if assay_type_enum else schema_name
    category = " / ".join(assay_category_enum) if assay_category_enum else "other"
    title += f" ({' / '.join(source_project_enum)})" if source_project_enum else ""

    is_deprecated = max_version_table_schema.get("deprecated", False)
    is_cedar = (
        max_version_table_schema.get("fields", [])[0]
        and type(max_version_table_schema.get("fields", [])[0]) == dict
        and max_version_table_schema.get("fields", [])[0].get("name", "") == "is_cedar"
    )
    is_draft = max_version_table_schema.get("draft", False)

    raw_base_url = "https://raw.githubusercontent.com/hubmapconsortium/" + (
        "ingest-validation-tools/main/docs"
        if not is_cedar
        else "dataset-metadata-spreadsheet/main"
    )

    optional_dir_description_md = (
        f"## Directory schemas\n{_make_dir_descriptions(directory_schemas, pipeline_infos)}"
        if directory_schemas
        else ""
    )

    optional_doc_link_md = (
        f'- [🔬 Background doc]({max_version_table_schema["doc_url"]}): '
        "More details about this type."
        if "doc_url" in max_version_table_schema
        else ""
    )

    optional_description_md = (
        max_version_table_schema["description_md"]
        if "description_md" in max_version_table_schema
        else ""
    )

    optional_release_date = (
        f", release date {max_version_table_schema['release_date']}"
        if "release_date" in max_version_table_schema
        else ""
    )

    template = Template((Path(__file__).parent / "docs.template").read_text())

    # If it is a draft, no link
    if (
        is_deprecated
        or is_draft
        or (
            is_cedar
            and max_version_table_schema.get("fields", [])[0].get("example", "") == ""
        )
    ):
        tsv_url = ""
        xlsx_url = ""
    # If it is a cedar template, link to the dataset-metadata-spreadsheet repo
    elif is_cedar:
        tsv_url = f"{raw_base_url}/{schema_name}/latest/{schema_name}.tsv"
        xlsx_url = f"{raw_base_url}/{schema_name}/latest/{schema_name}.xlsx"
    else:
        tsv_url = f"{raw_base_url}/{schema_name}/{get_tsv_name(schema_name, is_assay=is_assay)}"
        xlsx_url = f"{raw_base_url}/{schema_name}/{get_xlsx_name(schema_name, is_assay=is_assay)}"

    related_files_section_md = (
        f"""
- [📝 Excel template]({xlsx_url}): For metadata entry.
- [📝 TSV template]({tsv_url}): Alternative for metadata entry.
"""
        if tsv_url and xlsx_url
        else "Excel and TSV templates for this schema will be available "
        "when the draft next-generation schema, to be used in all "
        "future submissions, is finalized (no later than Sept. 30)."
    )

    if is_deprecated:
        related_files_section_md = ""

    return template.substitute(
        {
            "title": title,
            "schema_name": schema_name,
            "category": {
                "fish": "Fluorescence In Situ Hybridization (FISH)",
                "imaging": "Imaging",
                "clinical_imaging": "Clinical Imaging Modalities",
                "histology": "Histology",
                "mass_spectrometry": "Mass Spectrometry",
                "mass_spectrometry_imaging": "Imaging Mass Spectrometry (IMS)",
                "mxfbe": "Multiplex Fluorescence Based Experiment (MxFBE)",
                "organ": "Organ",
                "sample": "Sample",
                "sequence": "Sequence Assays",
                "single_cycle_fluorescence_microscopy": "Single-cycle Fluorescence Microscopy (SFM)",  # noqa E501
                "spatial_transcriptomics": "Spatial Transcriptomics",
                "other": "Other TSVs",
            }[category],
            "max_version": max_version,
            "all_versions_deprecated": all(
                schema.get("deprecated") for schema in table_schemas.values()
            ),
            "exclude_from_index": all(
                schema.get("exclude_from_index") for schema in table_schemas.values()
            ),
            "related_files_section_md": related_files_section_md,
            "current_version_md": _make_fields_md(
                max_version_table_schema,
                f"Version {max_version} "
                f'({f"use this one{optional_release_date}" if not is_deprecated else f"current"})',
                is_open=True,
            ),
            "previous_versions_md": "\n\n".join(
                [
                    _make_fields_md(table_schemas[str(v)], f"Version {v}")
                    for v in range(max_version - 1, min_version - 1, -1)
                    if str(v) in table_schemas
                ]
            ),
            "optional_dir_description_md": optional_dir_description_md,
            "optional_doc_link_md": optional_doc_link_md,
            "optional_description_md": optional_description_md,
        }
    )


def _make_fields_md(table_schema, title, is_open=False):
    """
    >>> schema = {'fields': [
    ...   'A head',
    ...   {
    ...     'name': 'a_name',
    ...     'description': 'A description'
    ...   }
    ... ]}
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
    """

    fields_md_list = []

    is_cedar = (
        len(table_schema["fields"]) > 0
        and type(table_schema["fields"][0]) == dict
        and table_schema["fields"][0].get("name", "") == "is_cedar"
    )

    if table_schema.get("deprecated"):
        title_html = f"<s>{title}</s> (deprecated)"
    elif table_schema.get("draft"):
        title_html = (
            f"<b>{title}</b> (draft - submission of data"
            f" prepared using this schema will be supported by Sept. 30)"
        )
    else:
        title_html = f"<b>{title}</b>"

    if not is_cedar:
        for field in table_schema["fields"]:
            if isinstance(field, str):
                fields_md_list.append(f"### {field}")
                continue
            table_md = _make_constraints_table(field)
            name = field["name"]
            fields_md_list.append(
                "\n".join(
                    [
                        f'<a name="{name}"></a>',
                        f"##### [`{name}`](#{name})",
                        _enrich_description(field),
                        table_md,
                    ]
                )
            )
        joined_list = "\n\n".join(fields_md_list)
        return f"""
<details markdown="1" {'open="true"' if is_open else ''}><summary>{title_html}</summary>

{_make_toc(joined_list) if is_open else ''}
{joined_list}

</details>
"""
    else:
        cedar_iri = table_schema["fields"][0]["example"]
        if cedar_iri:
            return f"""
<summary><a href="{cedar_iri}">{title_html}</a></summary>
"""
        elif cedar_iri == "" and table_schema.get("draft"):
            return f"""
<summary>{title_html} (TBD)</summary>
"""
        else:
            return f"""
<details markdown="1" {'open="true"' if is_open else ''}><summary>{title_html}</summary>
We do not expect to receive any new data of this assay type.
If you are planning to submit new data of this assay type, reach out to help@hubmapconsortium.org.
</details>
"""


def _make_constraints_table(field):
    """
    >>> field = {
    ...   'name': 'fake_field_units',
    ...   'type': 'fake type',
    ...   'constraints': {
    ...     'enum': ['a', 'b'],
    ...   },
    ...   'custom_constraints': {
    ...     'custom': 'fake',
    ...     'units_for': 'fake_field'
    ...   }
    ... }
    >>> print(_make_constraints_table(field))
    <BLANKLINE>
    | constraint | value |
    | --- | --- |
    | type | `fake type` |
    | enum | `a` or `b` |
    | custom | `fake` |
    | required if | `fake_field` present |
    """

    table_md_rows = ["| constraint | value |", "| --- | --- |"]
    for key, value in field.items():
        if key in ["type", "format"]:
            if key == "type" and value == "string":
                continue
            table_md_rows.append(f"| {key} | `{value}` |")
    if "constraints" in field:
        for key, value in field["constraints"].items():
            key_md = _make_key_md(key, value)
            value_md = _make_value_md(key, value)
            table_md_rows.append(f"| {key_md} | {value_md} |")
    if "custom_constraints" in field:
        for key, value in field["custom_constraints"].items():
            if key in ["sequence_limit", "forbid_na"]:
                # Applied to every field,
                # but we don't want to clutter the docs:
                continue
            key_md = _make_key_md(key, value)
            value_md = _make_value_md(key, value)
            table_md_rows.append(f"| {key_md} | {value_md} |")
    if len(table_md_rows) < 3:
        # Empty it, if there is no data.
        table_md_rows = []
    main_table_md = "\n".join(table_md_rows)

    ontology_table_md = (
        _make_ontology_table(field["constraints"]["enum"])
        if "constraints" in field and "enum" in field["constraints"]
        else ""
    )
    return "\n" + main_table_md + ontology_table_md


def _make_ontology_table(enum):
    if not isinstance(enum, dict):
        return ""
    table_md_rows = ["| term | URI |", "| --- | --- |"]
    for term, uri in enum.items():
        table_md_rows.append(f"| {term} | `{uri}` |")
    return "\n\nOntology terms:\n\n" + "\n".join(table_md_rows)


def _make_key_md(key, value):
    """
    >>> print(_make_key_md('pattern', 'some_reg_ex'))
    pattern (regular expression)

    >>> print(_make_key_md('other_keys', 'other_values'))
    other keys
    """
    if key == "pattern":
        return "pattern (regular expression)"
    if key == "units_for":
        return "required if"
    return key.replace("_", " ")


def _make_value_md(key, value):
    """
    >>> print(_make_value_md('not_enum', 'abc'))
    `abc`

    >>> print(_make_value_md('enum', ['A']))
    `A`

    >>> print(_make_value_md('enum', ['A', 'B']))
    `A` or `B`

    >>> print(_make_value_md('enum', ['A', 'B', 'C']))
    `A`, `B`, or `C`

    >>> print(_make_value_md('pattern', '^some|reg_?ex\\.$'))
    <code>^some&#124;reg_?ex\\.$</code>

    >>> print(_make_value_md('url', {'prefix': 'http://example.com/'}))
    prefix: <code>http://example.com/</code>

    """
    if key == "enum":
        backtick_list = [f"`{s}`" for s in value]
        if len(value) < 3:
            return " or ".join(backtick_list)
        backtick_list[-1] = f"or {backtick_list[-1]}"
        return ", ".join(backtick_list)
    if key == "pattern":
        return _html_code(value)
    if key == "url":
        return f'prefix: {_html_code(value["prefix"])}'
    if key == "units_for":
        return f"`{value}` present"
    return f"`{value}`"


def _html_code(re_string):
    """
    In Github pages, '`a|b`' can be used in a table,
    but in Github markdown preview, it will cause table cells to split.
    Instead, use HTML and a character entity.

    >>> original = 'gt >|lt <|amp &'
    >>> wrapped = _html_code(original)
    >>> print(wrapped)
    <code>gt &gt;&#124;lt &lt;&#124;amp &amp;</code>

    >>> unwrapped = html.unescape(wrapped.replace('<code>','').replace('</code>',''))
    >>> assert unwrapped == original
    """
    escaped = html.escape(re_string)
    pipe_escaped = escaped.replace("|", "&#124;")
    return f"<code>{pipe_escaped}</code>"


def _clean(s):
    return re.sub(r"\n+", "\n", s).strip()


def _make_toc(md):
    # Github should do this for us, but it doesn't.
    # Existing solutions expect a file, not a string,
    # or aren't Python at all, etc. Argh.
    # This is not good.
    """
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

    """
    lines = md.split("\n")
    headers = [
        re.sub(r"^#+\s*", "", re.sub(r".*\[(.*)\].*", r"\1", line))
        for line in lines
        if len(line) and line[0] == "#"
    ]
    in_details = False
    mds = []
    for h in headers:
        if "`" in h:
            mds.append(f"[{h}](#{h.lower().replace(' ', '-').replace('`', '')})<br>")
        else:
            if in_details:
                mds.append("\n</details>")
            mds.append(f'<details markdown="1"><summary>{h}</summary>\n')
            in_details = True
    if in_details:
        mds.append("</details>")
    joined_mds = "\n".join(mds)
    # If MD trails immediately after "</blockquote>",
    # it doesn't render correctly, so include a newline.
    return f'<blockquote markdown="1">\n\n{joined_mds}\n\n</blockquote>\n'


def _make_dir_descriptions(dir_schemas, pipeline_infos):
    """
    >>> dir_schema_0 = {
    ...     'files': [
    ...         {'pattern': 'required\\.txt', 'description': 'Required!'}
    ...     ]
    ... }
    >>> dir_schema_1 = {
    ...     'files': [
    ...         {'pattern': 'optional\\.txt', 'description': 'Optional!', 'required': False}
    ...     ]
    ... }
    >>> pipeline_infos = [{
    ...     "name": "Fake Pipeline",
    ...     "repo_url": "https://github.com/hubmapconsortium/fake",
    ...     "version_tag": "v1.2.3"
    ... }]
    >>> print(_make_dir_descriptions({'0': dir_schema_0, '1': dir_schema_1}, pipeline_infos))
    The HIVE will process each dataset with
    [Fake Pipeline v1.2.3](https://github.com/hubmapconsortium/fake/releases/tag/v1.2.3).
    <summary><b>Version 1 (use this one)</b></summary>
    <BLANKLINE>
    | pattern | required? | description |
    | --- | --- | --- |
    | <code>optional\\.txt</code> |  | Optional! |
    <BLANKLINE>
    <summary><b>Version 0</b></summary>
    <BLANKLINE>
    | pattern | required? | description |
    | --- | --- | --- |
    | <code>required\\.txt</code> | ✓ | Required! |
    <BLANKLINE>
    <BLANKLINE>
    """
    pipeline_infos_md = " and ".join(
        make_pipeline_link(info) for info in pipeline_infos
    )
    pipeline_blurb = (
        f"The HIVE will process each dataset with\n{pipeline_infos_md}.\n"
        if pipeline_infos
        else ""
    )

    sorted_items = sorted(dir_schemas.items(), key=lambda item: item[0], reverse=True)

    directory_descriptions = ""

    current_version = True

    for v, schema in sorted_items:

        if schema.get('draft', False):
            draft_link = schema.get('files', [])[0].get("draft_link", None)
            directory_descriptions += f'<summary><a href="{draft_link}"><b>Version {v}' \
                                      f'{" (use this one)" if current_version else ""}' \
                                      f'</b> (draft - submission of data prepared using this' \
                                      f' schema will be supported by Sept. 30) </a></summary>\n\n'
        else:
            directory_descriptions += (
                    f'<summary><b>Version {v}'
                    f'{" (use this one)" if current_version else ""}'
                    f'</b></summary>\n' + _make_dir_description(
                        schema['files'],
                        schema.get('deprecated', False)
                    ) + '\n\n')
        current_version = False

    return pipeline_blurb + directory_descriptions


def _make_dir_description(files, is_deprecated=False):
    """
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
    | <code>required\\.txt</code> | ✓ | **[QA/QC]** Required! |
    | <code>optional\\.txt</code> |  | Optional! |

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
    | <code>optional\\.txt</code> |  | Optional! |
    <BLANKLINE>
    </details>

    Examples add an extra column:

    >>> files = [
    ...   { 'pattern': '[A-Z]+\\d+', 'description': 'letters numbers', 'example': 'ABC123'},
    ...   { 'pattern': '[A-Z]', 'description': 'one letter, no example'},
    ... ]
    >>> print(_make_dir_description(files))
    <BLANKLINE>
    | pattern | required? | description |
    | --- | --- | --- |
    | <code>[A-Z]+\\d+</code> (example: <code>ABC123</code>) | ✓ | letters numbers |
    | <code>[A-Z]</code> | ✓ | one letter, no example |

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
    """

    for line in files:
        for k in line.keys():
            assert k in {
                "pattern",
                "required",
                "description",
                "example",
                "is_qa_qc",
            }, f'Unexpected key "{k}" in {line}'

    output = [
        """
| pattern | required? | description |
| --- | --- | --- |"""
    ]

    for line in files:
        row = []

        pattern = line["pattern"]
        pattern_md = _html_code(pattern)
        if "example" in line:
            example = line["example"]
            assert re.fullmatch(
                pattern, example
            ), f'Example "{example}" does not match pattern "{pattern}"'
            pattern_md += f" (example: {_html_code(example)})"
        row.append(pattern_md)

        required_md = "" if "required" in line and not line["required"] else "✓"
        row.append(required_md)

        qa_qc_md = "**[QA/QC]** " if "is_qa_qc" in line and line["is_qa_qc"] else ""
        description_md = qa_qc_md + line["description"]
        row.append(description_md)

        output.append("| " + " | ".join(row) + " |")
    table = "\n".join(output)

    if is_deprecated:
        return f'<details markdown="1"><summary>Deprecated</summary>\n{table}\n\n</details>'
    return table


def make_pipeline_link(info):
    """
    >>> info = {
    ...     "name": "Fake Pipeline",
    ...     "repo_url": "https://github.com/hubmapconsortium/fake",
    ...     "version_tag": "v1.2.3"
    ... }
    >>> print(make_pipeline_link(info))
    [Fake Pipeline v1.2.3](https://github.com/hubmapconsortium/fake/releases/tag/v1.2.3)
    """
    text = f"{info['name']} {info['version_tag']}"
    href = f"{info['repo_url']}/releases/tag/{info['version_tag']}"
    return f"[{text}]({href})"
