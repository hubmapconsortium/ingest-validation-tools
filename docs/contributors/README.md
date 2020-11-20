# contributors

Related files:

- [📝 TSV template](https://raw.githubusercontent.com/hubmapconsortium/ingest-validation-tools/master/docs/contributors/contributors-metadata.tsv): Use this to submit metadata.
- [💻 Source code](https://github.com/hubmapconsortium/ingest-validation-tools/edit/master/src/ingest_validation_tools/table-schemas/contributors.yaml): Make a PR if this doc should be updated.

## Table of contents
[`affiliation`](#affiliation)<br>
[`first_name`](#first_name)<br>
[`last_name`](#last_name)<br>
[`middle_name_or_initial`](#middle_name_or_initial)<br>
[`name`](#name)<br>
[`orcid_id`](#orcid_id)<br></details>

### `affiliation`
Institutional affiliation.



### `first_name`
First name.



### `last_name`
Last name.



### `middle_name_or_initial`
Middle name or initial.



### `name`
Name for display.



### `orcid_id`
ORCID ID of contributor.

| constraint | value |
| --- | --- |
| pattern (regular expression) | `\d{4}-\d{4}-\d{4}-\d{4}` |
| required | `True` |
