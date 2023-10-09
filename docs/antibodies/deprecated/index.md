---
title: antibodies
schema_name: antibodies
category: Other TSVs
all_versions_deprecated: False
exclude_from_index: False
layout: default
---

Related files:


- [📝 Excel template](https://raw.githubusercontent.com/hubmapconsortium/ingest-validation-tools/main/docs/antibodies/antibodies.xlsx): For metadata entry.
- [📝 TSV template](https://raw.githubusercontent.com/hubmapconsortium/ingest-validation-tools/main/docs/antibodies/antibodies.tsv): Alternative for metadata entry.


Changes:
- v1: Version number added.
- v2: Add concentration fields.

## Metadata schema


<details markdown="1" open="true"><summary><b>Version 2 (use this one)</b></summary>

<blockquote markdown="1">

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
[`conjugated_tag`](#conjugated_tag)<br>

</blockquote>

<a name="version"></a>
##### [`version`](#version)
Current version of metadata schema. Template provides the correct value.

| constraint | value |
| --- | --- |
| enum | `2` |
| required | `True` |

<a name="channel_id"></a>
##### [`channel_id`](#channel_id)
Structure of channel_id depends on assay type.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="antibody_name"></a>
##### [`antibody_name`](#antibody_name)
Anti-(target name) antibody. Not validated or used down-stream.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="rr_id"></a>
##### [`rr_id`](#rr_id)
The rr_id is a unique antibody identifier that comes from the Antibody Registry (https://antibodyregistry.org). Example: `AB_10002075`.

| constraint | value |
| --- | --- |
| pattern (regular expression) | <code>AB_\d+</code> |
| required | `True` |
| url | prefix: <code>https://scicrunch.org/resolver/RRID:</code> |

<a name="uniprot_accession_number"></a>
##### [`uniprot_accession_number`](#uniprot_accession_number)
The uniprot_accession_number is a unique identifier for proteins in the UniProt database (https://www.uniprot.org).

| constraint | value |
| --- | --- |
| required | `True` |
| url | prefix: <code>https://www.uniprot.org/uniprot/</code> |

<a name="lot_number"></a>
##### [`lot_number`](#lot_number)
The lot# is specific to the vendor. (eg: Abcam lot# GR3238979-1)

| constraint | value |
| --- | --- |
| required | `True` |

<a name="dilution"></a>
##### [`dilution`](#dilution)
Antibody solutions may be diluted according to the experimental protocol. Leave blank if not applicable. Example: `1/200`.

| constraint | value |
| --- | --- |
| required | `False` |
| pattern (regular expression) | <code>1/\d+</code> |

<a name="concentration_value"></a>
##### [`concentration_value`](#concentration_value)
The concentration value of the antibody preparation. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `False` |

<a name="concentration_unit"></a>
##### [`concentration_unit`](#concentration_unit)
The concentration units of the antibody preparation. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| enum | `ug/ml` |
| required | `False` |
| required if | `concentration_value` present |

<a name="conjugated_cat_number"></a>
##### [`conjugated_cat_number`](#conjugated_cat_number)
An antibody may be conjugated to a fluorescent tag or a metal tag for detection. Conjugated antibodies may be purchased from commercial providers. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |

<a name="conjugated_tag"></a>
##### [`conjugated_tag`](#conjugated_tag)
The name of the entity conjugated to the antibody. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |

</details>


<details markdown="1" ><summary><b>Version 1</b></summary>


<a name="version"></a>
##### [`version`](#version)
Current version of metadata schema. Template provides the correct value.

| constraint | value |
| --- | --- |
| enum | `1` |
| required | `True` |

<a name="channel_id"></a>
##### [`channel_id`](#channel_id)
Structure of channel_id depends on assay type.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="antibody_name"></a>
##### [`antibody_name`](#antibody_name)
Anti-(target name) antibody. Not validated or used down-stream.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="rr_id"></a>
##### [`rr_id`](#rr_id)
The rr_id is a unique antibody identifier that comes from the Antibody Registry (https://antibodyregistry.org). Example: `AB_10002075`.

| constraint | value |
| --- | --- |
| pattern (regular expression) | <code>AB_\d+</code> |
| required | `True` |
| url | prefix: <code>https://scicrunch.org/resolver/RRID:</code> |

<a name="uniprot_accession_number"></a>
##### [`uniprot_accession_number`](#uniprot_accession_number)
The uniprot_accession_number is a unique identifier for proteins in the UniProt database (https://www.uniprot.org).

| constraint | value |
| --- | --- |
| required | `True` |
| url | prefix: <code>https://www.uniprot.org/uniprot/</code> |

<a name="lot_number"></a>
##### [`lot_number`](#lot_number)
The lot# is specific to the vendor. (eg: Abcam lot# GR3238979-1)

| constraint | value |
| --- | --- |
| required | `True` |

<a name="dilution"></a>
##### [`dilution`](#dilution)
Antibody solutions may be diluted according to the experimental protocol. Leave blank if not applicable. Example: `1/200`.

| constraint | value |
| --- | --- |
| required | `False` |
| pattern (regular expression) | <code>1/\d+</code> |

<a name="conjugated_cat_number"></a>
##### [`conjugated_cat_number`](#conjugated_cat_number)
An antibody may be conjugated to a fluorescent tag or a metal tag for detection. Conjugated antibodies may be purchased from commercial providers. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |

<a name="conjugated_tag"></a>
##### [`conjugated_tag`](#conjugated_tag)
The name of the entity conjugated to the antibody. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |

</details>



<details markdown="1" ><summary><b>Version 0</b></summary>


<a name="channel_id"></a>
##### [`channel_id`](#channel_id)
Structure of channel_id depends on assay type.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="antibody_name"></a>
##### [`antibody_name`](#antibody_name)
Anti-(target name) antibody. Not validated or used down-stream.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="rr_id"></a>
##### [`rr_id`](#rr_id)
The rr_id is a unique antibody identifier that comes from the Antibody Registry (https://antibodyregistry.org). Example: `AB_10002075`.

| constraint | value |
| --- | --- |
| pattern (regular expression) | <code>AB_\d+</code> |
| required | `True` |
| url | prefix: <code>https://scicrunch.org/resolver/RRID:</code> |

<a name="uniprot_accession_number"></a>
##### [`uniprot_accession_number`](#uniprot_accession_number)
The uniprot_accession_number is a unique identifier for proteins in the UniProt database (https://www.uniprot.org).

| constraint | value |
| --- | --- |
| required | `True` |
| url | prefix: <code>https://www.uniprot.org/uniprot/</code> |

<a name="lot_number"></a>
##### [`lot_number`](#lot_number)
The lot# is specific to the vendor. (eg: Abcam lot# GR3238979-1)

| constraint | value |
| --- | --- |
| required | `True` |

<a name="dilution"></a>
##### [`dilution`](#dilution)
Antibody solutions may be diluted according to the experimental protocol. Leave blank if not applicable. Example: `1/200`.

| constraint | value |
| --- | --- |
| required | `False` |
| pattern (regular expression) | <code>1/\d+</code> |

<a name="conjugated_cat_number"></a>
##### [`conjugated_cat_number`](#conjugated_cat_number)
An antibody may be conjugated to a fluorescent tag or a metal tag for detection. Conjugated antibodies may be purchased from commercial providers. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |

<a name="conjugated_tag"></a>
##### [`conjugated_tag`](#conjugated_tag)
The name of the entity conjugated to the antibody. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |

</details>


<br>

