---
title: Sample Section
schema_name: sample-section
category: Sample
all_versions_deprecated: False
exclude_from_index: False
layout: default
---

Related files:


- [📝 Excel template](https://raw.githubusercontent.com/hubmapconsortium/dataset-metadata-spreadsheet/main/sample-section/latest/sample-section.xlsx): For metadata entry.
- [📝 TSV template](https://raw.githubusercontent.com/hubmapconsortium/dataset-metadata-spreadsheet/main/sample-section/latest/sample-section.tsv): Alternative for metadata entry.




## Metadata schema


<summary><a href="https://openview.metadatacenter.org/templates/https:%2F%2Frepo.metadatacenter.org%2Ftemplates%2F1f3d4b00-f6f2-48a4-8795-755be215f546"><b>Version 2 (use this one)</b></a></summary>


<details markdown="1" ><summary><b>Version 1</b></summary>


<a name="version"></a>
##### [`version`](#version)
The version of the sample metadata specification used in the submission.

| constraint | value |
| --- | --- |
| enum | `1` |
| required | `True` |

<a name="sample_id"></a>
##### [`sample_id`](#sample_id)
The unique Submission ID for the sample assigned by the ingest portal. An example value might be "VAN0010-LK-152-162".

| constraint | value |
| --- | --- |
| required | `True` |

<a name="type"></a>
##### [`type`](#type)
Denotes the type of sample, used to validate the field entries.

| constraint | value |
| --- | --- |
| enum | `section` |
| required | `True` |

<a name="source_storage_time_value"></a>
##### [`source_storage_time_value`](#source_storage_time_value)
The amount of time that elapsed between when the source was generated and this sample was derived from the source. This would, for example, include how long the source was stored in a freezer.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

<a name="source_storage_time_unit"></a>
##### [`source_storage_time_unit`](#source_storage_time_unit)
Time unit. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| enum | `min`, `hours`, `days`, or `years` |
| required | `False` |
| required if | `source_storage_time_value` present |

<a name="preparation_media"></a>
##### [`preparation_media`](#preparation_media)
The media used during preparation of the sample.

| constraint | value |
| --- | --- |
| enum | `PFA (4%)`, `Buffered Formalin (10% NBF)`, `Non-Buffered Formalin (FOR)`, `1 x PBS`, `OCT`, `CMC`, `MACS Tissue Storage Solution`, `RNAlater`, `Methanol`, `Non-aldehyde based without acetic acid (NAA)`, `Non-aldehyde with acetic acid (ACA)`, `PAXgene tissue (PXT)`, `Allprotect tissue reagent (ALL)`, or `None` |
| required | `True` |

<a name="preparation_condition"></a>
##### [`preparation_condition`](#preparation_condition)
The condition under which the preparation occurred, such as whether the sample was placed in dry ice during the preparation.

| constraint | value |
| --- | --- |
| enum | `frozen in liquid nitrogen`, `frozen in liquid nitrogen vapor`, `frozen in ice`, `frozen in dry ice`, `frozen at -20 C`, `ambient temperature`, or `unknown` |
| required | `True` |

<a name="processing_time_value"></a>
##### [`processing_time_value`](#processing_time_value)
The amount of time that elapsed from beginning of sampling to the first preservation (time from when received in lab to preservation). This would, for example, represent how long it took to cut the tissue and freeze it. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `False` |

<a name="processing_time_unit"></a>
##### [`processing_time_unit`](#processing_time_unit)
Time unit. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |
| enum | `min`, `hours`, or `days` |
| required if | `processing_time_value` present |

<a name="storage_media"></a>
##### [`storage_media`](#storage_media)
What was the sample preserved in.

| constraint | value |
| --- | --- |
| enum | `PFA (4%)`, `Buffered Formalin (10% NBF)`, `Non-Buffered Formalin (FOR)`, `1 x PBS`, `OCT Embedded`, `CMC Embedded`, `OCT Embedded Cryoprotected (sucrose)`, `Paraffin Embedded`, `MACS Tissue Storage Solution`, `RNAlater`, `Methanol`, `Tris-EDTA`, `70% ethanol`, `Serum + DMSO`, `DMSO (no serum)`, `PAXgene Tissue Kit (PXT)`, `Allprotect Tissue Reagent (ALL)`, `Sucrose Cryoprotection Solution`, `Carboxymethylcellulose (CMC)`, or `None` |
| required | `True` |

<a name="storage_method"></a>
##### [`storage_method`](#storage_method)
The method by which the sample was stored, after preparation and before the assay was performed.

| constraint | value |
| --- | --- |
| enum | `frozen in liquid nitrogen`, `frozen in liquid nitrogen vapor`, `frozen in ice`, `frozen in dry ice`, `frozen at -80 C`, `frozen at -20 C`, `refrigerator`, `ambient temperature`, `incubated at 37 C`, `none`, or `unknown` |
| required | `True` |

<a name="quality_criteria"></a>
##### [`quality_criteria`](#quality_criteria)
For example, RIN: 8.7. For suspensions, measured by visual inspection prior to cell lysis or defined by known parameters such as wells with several cells or no cells. This can be captured at a high level. "OK" or "not OK", or with more specificity such as "debris", "clump", "low clump". Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |

<a name="histological_report"></a>
##### [`histological_report`](#histological_report)
histopathological reporting of key variables that are important for the tissue (absence of necrosis, comment on composition, significant pathology description, high level inflammation/fibrosis assessment etc. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |

<a name="section_thickness_value"></a>
##### [`section_thickness_value`](#section_thickness_value)
Thickness of the section.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

<a name="section_thickness_unit"></a>
##### [`section_thickness_unit`](#section_thickness_unit)
Thickness unit. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| enum | `um`, `mm`, or `cm` |
| required | `False` |
| required if | `section_thickness_value` present |

<a name="section_index_number"></a>
##### [`section_index_number`](#section_index_number)
The index number for the section if the sample is a single section.

| constraint | value |
| --- | --- |
| type | `integer` |
| required | `True` |

<a name="area_value"></a>
##### [`area_value`](#area_value)
The area of a tissue section. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `False` |

<a name="area_unit"></a>
##### [`area_unit`](#area_unit)
Area unit. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |
| enum | `mm^2` or `um^2` |
| required if | `area_value` present |

<a name="notes"></a>
##### [`notes`](#notes)
Notes. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |

</details>


<br>

