# contributors

Related files:

- [📝 Excel template](https://raw.githubusercontent.com/hubmapconsortium/ingest-validation-tools/master/docs/contributors/contributors.xlsx): For metadata entry.
- [📝 TSV template](https://raw.githubusercontent.com/hubmapconsortium/ingest-validation-tools/master/docs/contributors/contributors.tsv): Alternative for metadata entry.
- [💻 Source code](https://github.com/hubmapconsortium/ingest-validation-tools/edit/master/src/ingest_validation_tools/table-schemas/contributors.yaml): Make a PR to update this doc.

## Table of contents
[`affiliation`](#affiliation)<br>
[`first_name`](#first_name)<br>
[`last_name`](#last_name)<br>
[`middle_name_or_initial`](#middle_name_or_initial)<br>
[`name`](#name)<br>
[`orcid_id`](#orcid_id)<br></details>

### `affiliation`
Institutional affiliation.

| constraint | value |
| --- | --- |
| required | `True` |

### `first_name`
First name.

| constraint | value |
| --- | --- |
| required | `True` |

### `last_name`
Last name.

| constraint | value |
| --- | --- |
| required | `True` |

### `middle_name_or_initial`
Middle name or initial. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |

### `name`
Name for display.

| constraint | value |
| --- | --- |
| required | `True` |

### `orcid_id`
ORCID ID of contributor. Example: `0000-0002-8928-741X`.

| constraint | value |
| --- | --- |
| pattern (regular expression) | `\d{4}-\d{4}-\d{4}-\d{3}[0-9X]` |
| required | `True` |
