# antibodies

Related files:

- [📝 TSV template](https://raw.githubusercontent.com/hubmapconsortium/ingest-validation-tools/master/docs/antibodies/antibodies-metadata.tsv): Use this to submit metadata.
- [💻 Source code](https://github.com/hubmapconsortium/ingest-validation-tools/edit/master/src/ingest_validation_tools/table-schemas/antibodies.yaml): Make a PR if this doc should be updated.

## Table of contents
[`channel_id`](#channel_id)<br>
[`antibody_name`](#antibody_name)<br>
[`rrr_id`](#rrr_id)<br>
[`uniprot_accession_number`](#uniprot_accession_number)<br>
[`lot_number`](#lot_number)<br>
[`dilution`](#dilution)<br>
[`conjugated_cat_number`](#conjugated_cat_number)<br>
[`conjugated_tag`](#conjugated_tag)<br></details>

### `channel_id`
The cycle/channel in which the protein was assessed with this antibody.

| constraint | value |
| --- | --- |
| type | `integer` |

### `antibody_name`
Anti-(target name) antibody. Not validated or used down-stream.



### `rrr_id`
The rr_id is a unique antibody identifier that comes from the Antibody Registry (https://antibodyregistry.org). Example: `AB_10002075`.

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



### `dilution`
Antibody solutions may be diluted according to the experimental protocol. Example: `1/200`.

| constraint | value |
| --- | --- |
| pattern (regular expression) | `1/\d+` |

### `conjugated_cat_number`
The catalog number for conjugated antibody.



### `conjugated_tag`
The name of the entity conjugated to the antibody.

