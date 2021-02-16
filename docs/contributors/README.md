# contributors

Related files:

- [📝 Excel template](https://raw.githubusercontent.com/hubmapconsortium/ingest-validation-tools/master/docs/contributors/contributors.xlsx): For metadata entry.
- [📝 TSV template](https://raw.githubusercontent.com/hubmapconsortium/ingest-validation-tools/master/docs/contributors/contributors.tsv): Alternative for metadata entry.
- [💻 Source code](https://github.com/hubmapconsortium/ingest-validation-tools/edit/master/src/ingest_validation_tools/table-schemas/contributors.yaml): Make a PR to update this doc.

Changes:
- v1: Version number added.

Previous versions:

- [v0](https://github.com/hubmapconsortium/ingest-validation-tools/tree/contributors-v0/docs/contributors) / [diff](https://github.com/hubmapconsortium/ingest-validation-tools/compare/contributors-v0...master)

## Table of contents
[`version`](#version)<br>
[`affiliation`](#affiliation)<br>
[`first_name`](#first_name)<br>
[`last_name`](#last_name)<br>
[`middle_name_or_initial`](#middle_name_or_initial)<br>
[`name`](#name)<br>
[`orcid_id`](#orcid_id)<br></details>

### `version`
Current version of metadata schema. Template provides the correct value.

| constraint | value |
| --- | --- |
| enum | `1` |
| required | `True` |

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
Middle name or initial.

| constraint | value |
| --- | --- |
| required | `True` |

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
