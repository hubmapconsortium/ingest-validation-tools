---
title: sample
schema_name: sample
category: Other TSVs
all_versions_deprecated: False
exclude_from_index: False
layout: default
permalink: /sample/
---

Related files:


- [📝 Excel template](https://raw.githubusercontent.com/hubmapconsortium/ingest-validation-tools/main/docs/sample/sample.xlsx): For metadata entry.
- [📝 TSV template](https://raw.githubusercontent.com/hubmapconsortium/ingest-validation-tools/main/docs/sample/sample.tsv): Alternative for metadata entry.




## Metadata schema


<details markdown="1" open="true"><summary><b>Version 0 (use this one)</b></summary>

<blockquote markdown="1">

<details markdown="1"><summary>IDs</summary>

[`sample_id`](#sample_id)<br>

</details>
<details markdown="1"><summary>Donor</summary>

[`vital_state`](#vital_state)<br>
[`health_status`](#health_status)<br>

</details>
<details markdown="1"><summary>Medical Procedure</summary>

[`organ_condition`](#organ_condition)<br>
[`procedure_date`](#procedure_date)<br>
[`perfusion_solution`](#perfusion_solution)<br>
[`pathologist_report`](#pathologist_report)<br>
[`warm_ischemia_time_value`](#warm_ischemia_time_value)<br>
[`warm_ischemia_time_unit`](#warm_ischemia_time_unit)<br>
[`cold_ischemia_time_value`](#cold_ischemia_time_value)<br>
[`cold_ischemia_time_unit`](#cold_ischemia_time_unit)<br>

</details>
<details markdown="1"><summary>Biospecimen</summary>

[`specimen_preservation_temperature`](#specimen_preservation_temperature)<br>
[`specimen_quality_criteria`](#specimen_quality_criteria)<br>
[`specimen_tumor_distance_value`](#specimen_tumor_distance_value)<br>
[`specimen_tumor_distance_unit`](#specimen_tumor_distance_unit)<br>
</details>

</blockquote>

### IDs

<a name="sample_id"></a>
##### [`sample_id`](#sample_id)
(No description for this field was supplied.) Example: `VAN0010-LK-152-162`.

| constraint | value |
| --- | --- |
| required | `True` |
| pattern (regular expression) | <code>([A-Z]+[0-9]+)-[A-Z]{2}\d*(-\d+)+(_\d+)?</code> |

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
| required if | `warm_ischemia_time_value` present |

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
| required if | `cold_ischemia_time_value` present |

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
| required if | `specimen_tumor_distance_value` present |

</details>



<br>

