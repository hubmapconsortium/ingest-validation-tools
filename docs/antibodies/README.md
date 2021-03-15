# antibodies

Related files:

- [📝 Excel template](https://raw.githubusercontent.com/hubmapconsortium/ingest-validation-tools/master/docs/antibodies/antibodies.xlsx): For metadata entry.
- [📝 TSV template](https://raw.githubusercontent.com/hubmapconsortium/ingest-validation-tools/master/docs/antibodies/antibodies.tsv): Alternative for metadata entry.
- [💻 Metadata schema](https://github.com/hubmapconsortium/ingest-validation-tools/edit/master/src/ingest_validation_tools/table-schemas/antibodies.yaml): To update metadata fields.


Changes:
- v1: Version number added.
- v2: Add concentration fields.




## Metadata schema
### Version 2 (Current)

[`version`](#version)<br>
[`channel_id`](#channel_id)<br>
[`antibody_name`](#antibody_name)<br>
[`rr_id`](#rr_id)<br>
[`uniprot_accession_number`](#uniprot_accession_number)<br>
[`lot_number`](#lot_number)<br>
[`dilution`](#dilution)<br>
[`concentration_value`](#concentration_value)<br>
[`concentration_unit`](#concentration_unit)<br>
[`conjugated_cat_number`](#conjugated_cat_number)<br>
[`conjugated_tag`](#conjugated_tag)<br></details>

<details open="true"><summary>Version 2</summary>

### `version`
Current version of metadata schema. Template provides the correct value.

| constraint | value |
| --- | --- |
| enum | `2` |
| required | `True` |

### `channel_id`
Structure of channel_id depends on assay type.

| constraint | value |
| --- | --- |
| required | `True` |

### `antibody_name`
Anti-(target name) antibody. Not validated or used down-stream.

| constraint | value |
| --- | --- |
| required | `True` |

### `rr_id`
The rr_id is a unique antibody identifier that comes from the Antibody Registry (https://antibodyregistry.org). Example: `AB_10002075`.

| constraint | value |
| --- | --- |
| pattern (regular expression) | `AB_\d+` |
| required | `True` |
| url | prefix: `https://scicrunch.org/resolver/RRID:` |

### `uniprot_accession_number`
The uniprot_accession_number is a unique identifier for proteins in the UniProt database (https://www.uniprot.org).

| constraint | value |
| --- | --- |
| required | `True` |
| url | prefix: `https://www.uniprot.org/uniprot/` |

### `lot_number`
The lot# is specific to the vendor. (eg: Abcam lot# GR3238979-1)

| constraint | value |
| --- | --- |
| required | `True` |

### `dilution`
Antibody solutions may be diluted according to the experimental protocol. Leave blank if not applicable. Example: `1/200`.

| constraint | value |
| --- | --- |
| required | `False` |
| pattern (regular expression) | `1/\d+` |

### `concentration_value`
The concentration value of the antibody preparation. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `False` |

### `concentration_unit`
The concentration units of the antibody preparation. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| enum | `ug/ml` |
| required | `False` |
| units for | `concentration_value` |

### `conjugated_cat_number`
An antibody may be conjugated to a fluorescent tag or a metal tag for detection. Conjugated antibodies may be purchased from commercial providers. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |

### `conjugated_tag`
The name of the entity conjugated to the antibody. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |

</details>


### Previous Versions

TODO: previous_versions_md