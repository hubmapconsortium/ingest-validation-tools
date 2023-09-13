---
title: Organ
schema_name: organ
category: Organ
all_versions_deprecated: False
exclude_from_index: False
layout: default
---

Related files:


- [📝 Excel template](https://raw.githubusercontent.com/hubmapconsortium/dataset-metadata-spreadsheet/main/organ/latest/organ.xlsx): For metadata entry.
- [📝 TSV template](https://raw.githubusercontent.com/hubmapconsortium/dataset-metadata-spreadsheet/main/organ/latest/organ.tsv): Alternative for metadata entry.




## Metadata schema


<summary><a href="https://openview.metadatacenter.org/templates/https:%2F%2Frepo.metadatacenter.org%2Ftemplates%2F8377b9ba-97bb-4b26-a2ac-2b88d756450f"><b>Version 3 (use this one)</b></a></summary>


<details markdown="1" ><summary><b>Version 2</b></summary>


<a name="organ_id"></a>
##### [`organ_id`](#organ_id)
Unique HuBMAP identifier for the organ. This can be found in the Submission ID section of a registered donor on the Ingest UI. Example: `TEST0001-RK`.

| constraint | value |
| --- | --- |
| required | `True` |
| pattern (regular expression) | <code>([A-Z]+[0-9]+)-[A-Z]{2}</code> |

<a name="lab_id"></a>
##### [`lab_id`](#lab_id)
An internal field labs can use it to add whatever ID(s) they want or need for dataset validation and tracking. This could be a single ID (e.g., "Visium_9OLC_A4_S1") or a delimited list of IDs (e.g., “9OL; 9OLC.A2; Visium_9OLC_A4_S1”). This field will not be accessible to anyone outside of the consortium and no effort will be made to check if IDs provided by one data provider are also used by another. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |

<a name="laterality"></a>
##### [`laterality`](#laterality)
The side of the body from which the organ came. This would be 'N/A' for blood, whereas an organ like the uterus would have a value of 'midline'.

| constraint | value |
| --- | --- |
| required | `True` |
| enum | `Left`, `Right`, `Midline`, or `N/A` |

<a name="organ_condition"></a>
##### [`organ_condition`](#organ_condition)
Health status of the organ at the time of sample recovery.

| constraint | value |
| --- | --- |
| required | `True` |
| enum | `Healthy` or `Diseased` |

<a name="perfusion_solution"></a>
##### [`perfusion_solution`](#perfusion_solution)
Type of solution that was used to perfuse the organ. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |
| enum | `Miltenyi Tissue Preservation Buffer`, `UWS`, `HTK`, `Belzer MPS/KPS`, `None`, or `Unknown` |

<a name="transport_solution"></a>
##### [`transport_solution`](#transport_solution)
Type of solution used during transport. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |
| enum | `RPMI`, `PBS (1x)`, `Miltenyi Tissue Preservation Buffer`, `UWS`, `HTK`, `Belzer MPS/KPS`, `Saline (Buffered)`, `DMEM`, `None`, or `Unknown` |

<a name="warm_ischemic_time_value"></a>
##### [`warm_ischemic_time_value`](#warm_ischemic_time_value)
Time interval from interruption of blood supply of tissue to cooling to 4C: For organ donor: cessation of blood flow to perfusion of organ (cooled to 4C) For surgical specimen/biopsy: cessation of blood flow to specimen (time biopsy taken or blood supply is interrupted) to cooling of specimen to 4C.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

<a name="warm_ischemic_time_unit"></a>
##### [`warm_ischemic_time_unit`](#warm_ischemic_time_unit)
Time unit for the previous element. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |
| enum | `hours` or `minutes` |
| required if | `warm_ischemic_time_value` present |

<a name="cold_ischemic_time_value"></a>
##### [`cold_ischemic_time_value`](#cold_ischemic_time_value)
Time interval from cooling to 4C to final preservation. For organ donor: organ preservation flush (cooled to 4C) to final preservation (freezing or fixation). For surgical specimen/biopsy: time specimen is placed at 4C to final preservation (freezing or fixation.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

<a name="cold_ischemic_time_unit"></a>
##### [`cold_ischemic_time_unit`](#cold_ischemic_time_unit)
Time unit for the previous element. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |
| enum | `hours` or `minutes` |
| required if | `cold_ischemic_time_value` present |

<a name="total_ischemic_time_value"></a>
##### [`total_ischemic_time_value`](#total_ischemic_time_value)
Total time prior to tissue dissection.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

<a name="total_ischemic_time_unit"></a>
##### [`total_ischemic_time_unit`](#total_ischemic_time_unit)
Time unit for the previous element. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |
| enum | `hours` or `minutes` |
| required if | `total_ischemic_time_value` present |

<a name="pathology_report"></a>
##### [`pathology_report`](#pathology_report)
General pathologist report. Further details on organ level QC checks.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="organ_weight_value"></a>
##### [`organ_weight_value`](#organ_weight_value)
The total organ weight. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `False` |

<a name="weight_unit"></a>
##### [`weight_unit`](#weight_unit)
Weight unit. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |
| enum | `g` or `kg` |

<a name="organ_height_value"></a>
##### [`organ_height_value`](#organ_height_value)
The height value of the organ. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `False` |

<a name="organ_height_unit"></a>
##### [`organ_height_unit`](#organ_height_unit)
Height unit. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |
| enum | `cm` or `mm` |
| required if | `organ_height_value` present |

<a name="organ_width_value"></a>
##### [`organ_width_value`](#organ_width_value)
The width value of the organ. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `False` |

<a name="organ_width_unit"></a>
##### [`organ_width_unit`](#organ_width_unit)
Width unit. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |
| enum | `cm` or `mm` |
| required if | `organ_width_value` present |

<a name="organ_length_value"></a>
##### [`organ_length_value`](#organ_length_value)
The length value of the organ. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `False` |

<a name="organ_length_unit"></a>
##### [`organ_length_unit`](#organ_length_unit)
Length unit. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |
| enum | `cm` or `mm` |
| required if | `organ_length_value` present |

<a name="organ_volume_value"></a>
##### [`organ_volume_value`](#organ_volume_value)
A measure of the organ volume via buffer/water displacement by submerging the organ to reflect the volume of the organ. (May reflect gas trapping in lung with obstructed airways.) Leave blank if not applicable.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `False` |

<a name="organ_volume_unit"></a>
##### [`organ_volume_unit`](#organ_volume_unit)
Volume unit. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |
| enum | `ml` |
| required if | `organ_volume_value` present |

</details>


<br>

