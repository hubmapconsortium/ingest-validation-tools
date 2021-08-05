---
title: organ
schema_name: organ
category: Other TSVs
all_versions_deprecated: False
layout: default
---

Related files:

- [📝 Excel template](https://raw.githubusercontent.com/hubmapconsortium/ingest-validation-tools/main/docs/organ/organ.xlsx): For metadata entry.
- [📝 TSV template](https://raw.githubusercontent.com/hubmapconsortium/ingest-validation-tools/main/docs/organ/organ.tsv): Alternative for metadata entry.

See also the sample schema.



## Metadata schema


<details markdown="1" open="true"><summary><b>Version 1 (current)</b></summary>

<blockquote markdown="1">

[`version`](#version)<br>
<details markdown="1"><summary>IDs</summary>

[`donor_id`](#donor_id)<br>
[`organ_id`](#organ_id)<br>

</details>
<details markdown="1"><summary>Details</summary>

[`organ`](#organ)<br>
[`organ_condition`](#organ_condition)<br>
[`organ_source`](#organ_source)<br>
[`perfusion_solution`](#perfusion_solution)<br>
[`transport_solution`](#transport_solution)<br>
[`warm_ischemic_time_value`](#warm_ischemic_time_value)<br>
[`warm_ischemic_time_unit`](#warm_ischemic_time_unit)<br>
[`cold_ischemic_time_value`](#cold_ischemic_time_value)<br>
[`cold_ischemic_time_unit`](#cold_ischemic_time_unit)<br>
[`organ_weight_value`](#organ_weight_value)<br>
[`organ_weight_unit`](#organ_weight_unit)<br>
[`pathologist_report`](#pathologist_report)<br>
[`height_value`](#height_value)<br>
[`height_unit`](#height_unit)<br>
[`width_value`](#width_value)<br>
[`width_unit`](#width_unit)<br>
[`length_value`](#length_value)<br>
[`length_unit`](#length_unit)<br>
[`organ_preparation_protocols_io_doi`](#organ_preparation_protocols_io_doi)<br>
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

<a name="donor_id"></a>
##### [`donor_id`](#donor_id)
Unique identifier for the organ donor.

| constraint | value |
| --- | --- |
| pattern (regular expression) | `([A-Z]+[0-9]+)-[A-Z]{2}\d*(-\d+)+(_\d+)?` |
| required | `True` |

<a name="organ_id"></a>
##### [`organ_id`](#organ_id)
Unique identifier for the organ. Currently referred to as "sample ID".

| constraint | value |
| --- | --- |
| pattern (regular expression) | `([A-Z]+[0-9]+)-[A-Z]{2}\d*(-\d+)+(_\d+)?` |
| required | `True` |

### Details

<a name="organ"></a>
##### [`organ`](#organ)
Organ from which the tissue is going to be taken.

| constraint | value |
| --- | --- |
| enum | `TODO` |
| required | `True` |

<a name="organ_condition"></a>
##### [`organ_condition`](#organ_condition)
Health status of the organ at the time of sample recovery.

| constraint | value |
| --- | --- |
| enum | `TODO` |
| required | `True` |

<a name="organ_source"></a>
##### [`organ_source`](#organ_source)
TODO.

| constraint | value |
| --- | --- |
| enum | `surgery`, `organ donor`, or `autopsy` |
| required | `True` |

<a name="perfusion_solution"></a>
##### [`perfusion_solution`](#perfusion_solution)
Type of solution that was used to perfuse the organ. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |
| enum | `RPMI`, `PBS, Miltenyi Tissue Preservation Buffer`, `UWS`, `HTK`, `Belzer MPS/KPS`, or `Unknown` |

<a name="transport_solution"></a>
##### [`transport_solution`](#transport_solution)
Type of solution used during transport. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |
| enum | `RPMI`, `PBS, Miltenyi Tissue Preservation Buffer`, `UWS`, `HTK`, `Belzer MPS/KPS`, or `Unknown` |

<a name="warm_ischemic_time_value"></a>
##### [`warm_ischemic_time_value`](#warm_ischemic_time_value)
Time interval between cessation of blood flow and cooling to 4C. (Preservation solution flushed time) - (Organ out time)

| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

<a name="warm_ischemic_time_unit"></a>
##### [`warm_ischemic_time_unit`](#warm_ischemic_time_unit)
TODO. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| enum | `minute` |
| required | `False` |
| units for | `warm_ischemic_time_value` |

<a name="cold_ischemic_time_value"></a>
##### [`cold_ischemic_time_value`](#cold_ischemic_time_value)
Time interval on ice to the start of preservation protocol. (Specimen acquisition start time) - (Preservation solution flushed time)

| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

<a name="cold_ischemic_time_unit"></a>
##### [`cold_ischemic_time_unit`](#cold_ischemic_time_unit)
TODO. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| enum | `minute` |
| required | `False` |
| units for | `cold_ischemic_time_value` |

<a name="organ_weight_value"></a>
##### [`organ_weight_value`](#organ_weight_value)
The total organ weight.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

<a name="organ_weight_unit"></a>
##### [`organ_weight_unit`](#organ_weight_unit)
TODO. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| enum | `g` |
| required | `False` |
| units for | `organ_weight_value` |

<a name="pathologist_report"></a>
##### [`pathologist_report`](#pathologist_report)
Further details on organ level QC checks.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="height_value"></a>
##### [`height_value`](#height_value)
Organ specific dimension. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `False` |

<a name="height_unit"></a>
##### [`height_unit`](#height_unit)
TODO. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| enum | `cm` |
| required | `False` |
| units for | `height_value` |

<a name="width_value"></a>
##### [`width_value`](#width_value)
Organ specific dimension. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `False` |

<a name="width_unit"></a>
##### [`width_unit`](#width_unit)
TODO. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| enum | `cm` |
| required | `False` |
| units for | `width_value` |

<a name="length_value"></a>
##### [`length_value`](#length_value)
Organ specific dimension. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `False` |

<a name="length_unit"></a>
##### [`length_unit`](#length_unit)
TODO. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| enum | `cm` |
| required | `False` |
| units for | `length_value` |

<a name="organ_preparation_protocols_io_doi"></a>
##### [`organ_preparation_protocols_io_doi`](#organ_preparation_protocols_io_doi)
TODO.

| constraint | value |
| --- | --- |
| required | `True` |
| pattern (regular expression) | `10\.17504/.*` |
| url | prefix: `https://dx.doi.org/` |

<a name="notes"></a>
##### [`notes`](#notes)
TODO.

| constraint | value |
| --- | --- |
| required | `True` |

</details>

