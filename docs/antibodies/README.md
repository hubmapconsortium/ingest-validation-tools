# antibodies

Related files:

- [📝 TSV template](https://raw.githubusercontent.com/hubmapconsortium/ingest-validation-tools/master/docs/antibodies/antibodies-metadata.tsv): Use this to submit metadata.
- [💻 Source code](https://github.com/hubmapconsortium/ingest-validation-tools/edit/master/src/ingest_validation_tools/table-schemas/antibodies.yaml): Make a PR if this doc should be updated.

## Table of contents
[`antibody_name`](#antibody_name)<br>
[`rrr_id`](#rrr_id)<br>
[`uniprot_accession_number`](#uniprot_accession_number)<br>
[`lot_number`](#lot_number)<br>
[`validation_report_location`](#validation_report_location)<br>
[`assay`](#assay)<br>
[`dilution`](#dilution)<br>
[`conjugated_cat_number`](#conjugated_cat_number)<br>
[`conjugated_tag`](#conjugated_tag)<br></details>

### `antibody_name`
Anti-(target name) antibody.



### `rrr_id`
The rrr_id is a unique antibody identifier that comes from the Antibody Registry (https://antibodyregistry.org). Example: `AB_10002075`.

| constraint | value |
| --- | --- |
| pattern (regular expression) | `AB_\d+` |

### `uniprot_accession_number`
The uniprot_accession_number is a unique identifier for proteins in the UniProt database (https://www.uniprot.org). Example: `P0DTC1`.

| constraint | value |
| --- | --- |
| pattern (regular expression) | `P[0-9A-Z]+` |

### `lot_number`
The lot# is specific to the vendor. (eg: Abcam lot# GR3238979-1)



### `validation_report_location`
TODO.



### `assay`
TODO.



### `dilution`
Antibody solutions may be diluted according to the experimental protocol. Example: `1/200`.

| constraint | value |
| --- | --- |
| pattern (regular expression) | `1/\d+` |

### `conjugated_cat_number`
The catalog number for conjugated antibody.



### `conjugated_tag`
TODO.


