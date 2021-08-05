---
title: sample
schema_name: sample
category: Other TSVs
all_versions_deprecated: False
layout: default
---

Related files:

- [📝 Excel template](https://raw.githubusercontent.com/hubmapconsortium/ingest-validation-tools/main/docs/sample/sample.xlsx): For metadata entry.
- [📝 TSV template](https://raw.githubusercontent.com/hubmapconsortium/ingest-validation-tools/main/docs/sample/sample.tsv): Alternative for metadata entry.

Sample schema v1 is a complete rewrite; There are fields that correspond to v0, but these will need to be mapped at index-time. See also the organ schema.



## Metadata schema


<details markdown="1" open="true"><summary><b>Version 1 (current)</b></summary>

<blockquote markdown="1">

[`version`](#version)<br>
<details markdown="1"><summary>IDs</summary>

[`source_id`](#source_id)<br>
[`sample_id`](#sample_id)<br>

</details>
<details markdown="1"><summary>Details</summary>

[`anatomical_region`](#anatomical_region)<br>
[`tissue`](#tissue)<br>
[`weight_value`](#weight_value)<br>
[`weight_unit`](#weight_unit)<br>
[`sample_pathology_distance_value`](#sample_pathology_distance_value)<br>
[`sample_tumor_distance_unit`](#sample_tumor_distance_unit)<br>
[`sample_preparation_protocols_io_doi`](#sample_preparation_protocols_io_doi)<br>
[`sample_preparation_media`](#sample_preparation_media)<br>
[`sample_preparation_temperature`](#sample_preparation_temperature)<br>
[`sample_storage_temperature`](#sample_storage_temperature)<br>
[`sample_quality_criteria`](#sample_quality_criteria)<br>
[`histological_report`](#histological_report)<br>
[`notes`](#notes)<br>
</details>

</blockquote>

<a name="version"></a>
##### [`version`](#version)
Current version of schema.

| constraint | value |
| --- | --- |
| enum | `1` |
| required | `True` |

### IDs

<a name="source_id"></a>
##### [`source_id`](#source_id)
Unique identifier for the source (parent) from which the sample was taken.

| constraint | value |
| --- | --- |
| pattern (regular expression) | `([A-Z]+[0-9]+)-[A-Z]{2}\d*(-\d+)+(_\d+)?` |
| required | `True` |

<a name="sample_id"></a>
##### [`sample_id`](#sample_id)
Unique identifier for the sample. Currently referred to as "tissue ID".

| constraint | value |
| --- | --- |
| pattern (regular expression) | `([A-Z]+[0-9]+)-[A-Z]{2}\d*(-\d+)+(_\d+)?` |
| required | `True` |

### Details

<a name="anatomical_region"></a>
##### [`anatomical_region`](#anatomical_region)
Region within the organ. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |
| enum | `TODO` |

<a name="tissue"></a>
##### [`tissue`](#tissue)
Organ specific tissue.

| constraint | value |
| --- | --- |
| enum | `TODO` |
| required | `True` |

<a name="weight_value"></a>
##### [`weight_value`](#weight_value)
Sample weight. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `False` |

<a name="weight_unit"></a>
##### [`weight_unit`](#weight_unit)
Sample weight. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| enum | `g` |
| required | `False` |
| units for | `weight_value` |

<a name="sample_pathology_distance_value"></a>
##### [`sample_pathology_distance_value`](#sample_pathology_distance_value)
If surgical sample, how far from the pathology was the sample obtained. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `False` |

<a name="sample_tumor_distance_unit"></a>
##### [`sample_tumor_distance_unit`](#sample_tumor_distance_unit)
Distance unit.

| constraint | value |
| --- | --- |
| enum | `cm` |
| required | `True` |
| units for | `sample_pathology_distance_value` |

<a name="sample_preparation_protocols_io_doi"></a>
##### [`sample_preparation_protocols_io_doi`](#sample_preparation_protocols_io_doi)
TODO.

| constraint | value |
| --- | --- |
| required | `True` |
| pattern (regular expression) | `10\.17504/.*` |
| url | prefix: `https://dx.doi.org/` |

<a name="sample_preparation_media"></a>
##### [`sample_preparation_media`](#sample_preparation_media)
What was the sample preserved in.

| constraint | value |
| --- | --- |
| enum | `fresh`, `snap frozen`, `fresh frozen OCT`, `FFPE`, `RNAlater`, `4% PFA`, `fixed frozen OCT`, `Cellfreezing media`, `CMC`, or `10% NBF` |
| required | `True` |

<a name="sample_preparation_temperature"></a>
##### [`sample_preparation_temperature`](#sample_preparation_temperature)
The temperature for the preparation process.

| constraint | value |
| --- | --- |
| enum | `Liquid Nitrogen`, `Liquid Nitrogen Vapor`, `Freezer (-80 Celsius)`, `Freezer (-20 Celsius)`, `Refrigerator (4 Celsius)`, or `Room Temperature` |
| required | `True` |

<a name="sample_storage_temperature"></a>
##### [`sample_storage_temperature`](#sample_storage_temperature)
The temperature during storage, after preparation and before the assay is performed.

| constraint | value |
| --- | --- |
| enum | `Liquid Nitrogen`, `Liquid Nitrogen Vapor`, `Freezer (-80 Celsius)`, `Freezer (-20 Celsius)`, `Refrigerator (4 Celsius)`, or `Room Temperature` |
| required | `True` |

<a name="sample_quality_criteria"></a>
##### [`sample_quality_criteria`](#sample_quality_criteria)
For example, RIN: 8.7. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |

<a name="histological_report"></a>
##### [`histological_report`](#histological_report)
Histopathological reporting of key variables that are important for the tissue (absence of necrosis, comment on composition, significant pathology description, high level inflammation/fibrosis assessment, etc.) Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |

<a name="notes"></a>
##### [`notes`](#notes)
TODO. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| enum | `left` or `right` |
| required | `False` |

</details>


<details markdown="1" ><summary><b>Version 0</b></summary>


### IDs

<a name="sample_id"></a>
##### [`sample_id`](#sample_id)
(No description for this field was supplied.)

| constraint | value |
| --- | --- |
| required | `True` |
| pattern (regular expression) | `([A-Z]+[0-9]+)-[A-Z]{2}\d*(-\d+)+(_\d+)?` |

### Donor

<a name="vital_state"></a>
##### [`vital_state`](#vital_state)
Identify the vital state of the donor.

| constraint | value |
| --- | --- |
| required | `True` |
| enum | `living` or `deceased` |

<a name="health_status"></a>
##### [`health_status`](#health_status)
Patient's baseline physical condition prior to immediate event leading to organ/tissue acquisition. For example, if a relatively healthy patient suffers trauma, and as a result of reparative surgery, a tissue sample is collected, the subject will be deemed “relatively healthy”.   Likewise, a relatively healthy subject may have experienced trauma leading to brain death.  As a result of organ donation, a sample is collected.  In this scenario, the subject is deemed “relatively healthy.”.

| constraint | value |
| --- | --- |
| required | `True` |
| enum | `cancer`, `relatively healthy`, or `chronic illness` |

### Medical Procedure

<a name="organ_condition"></a>
##### [`organ_condition`](#organ_condition)
Health status of the organ at the time of sample recovery.

| constraint | value |
| --- | --- |
| required | `True` |
| enum | `healthy` or `diseased` |

<a name="procedure_date"></a>
##### [`procedure_date`](#procedure_date)
Date of procedure to procure organ.

| constraint | value |
| --- | --- |
| type | `date` |
| format | `%Y-%m-%d` |
| required | `True` |

<a name="perfusion_solution"></a>
##### [`perfusion_solution`](#perfusion_solution)
Type of solution that was used to perfuse the organ.

| constraint | value |
| --- | --- |
| required | `True` |
| enum | `UWS`, `HTK`, `Belzer MPS/KPS`, `Formalin`, `Perfadex`, `Unknown`, or `None` |

<a name="pathologist_report"></a>
##### [`pathologist_report`](#pathologist_report)
Further details on organ level QC checks.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="warm_ischemia_time_value"></a>
##### [`warm_ischemia_time_value`](#warm_ischemia_time_value)
Time interval between cessation of blood flow and cooling to 4C. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `False` |

<a name="warm_ischemia_time_unit"></a>
##### [`warm_ischemia_time_unit`](#warm_ischemia_time_unit)
Time unit. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |
| enum | `minutes` |
| units for | `warm_ischemia_time_value` |

<a name="cold_ischemia_time_value"></a>
##### [`cold_ischemia_time_value`](#cold_ischemia_time_value)
Time interval on ice to the start of preservation protocol. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `False` |

<a name="cold_ischemia_time_unit"></a>
##### [`cold_ischemia_time_unit`](#cold_ischemia_time_unit)
Time unit. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |
| enum | `minutes` |
| units for | `cold_ischemia_time_value` |

### Biospecimen

<a name="specimen_preservation_temperature"></a>
##### [`specimen_preservation_temperature`](#specimen_preservation_temperature)
The temperature of the medium during the preservation process.

| constraint | value |
| --- | --- |
| required | `True` |
| enum | `Liquid Nitrogen`, `Liquid Nitrogen Vapor`, `Freezer (-80 Celsius)`, `Freezer (-20 Celsius)`, `Refrigerator (4 Celsius)`, or `Room Temperature` |

<a name="specimen_quality_criteria"></a>
##### [`specimen_quality_criteria`](#specimen_quality_criteria)
For example, RIN: 8.7. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |

<a name="specimen_tumor_distance_value"></a>
##### [`specimen_tumor_distance_value`](#specimen_tumor_distance_value)
If surgical sample, how far from the tumor was the sample obtained from. Typically a number of centimeters. Leave blank if not applicable or unknown. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `False` |

<a name="specimen_tumor_distance_unit"></a>
##### [`specimen_tumor_distance_unit`](#specimen_tumor_distance_unit)
Distance unit. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |
| enum | `cm` |
| units for | `specimen_tumor_distance_value` |

</details>
