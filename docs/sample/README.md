# sample

Related files:
- [🔬 Background doc](TODO): More details about this type.
- [📝 TSV template](https://raw.githubusercontent.com/hubmapconsortium/ingest-validation-tools/master/docs/sample/sample-metadata.tsv): Use this to submit metadata.
- [💻 Source code](https://github.com/hubmapconsortium/ingest-validation-tools/edit/master/src/ingest_validation_tools/table-schemas/level-2/sample.yaml): Make a PR if this doc should be updated.

## Table of contents
<details><summary>IDs</summary>

[`sample_id`](#sample_id)<br>
</details>

<details><summary>Donor</summary>

[`vital_state`](#vital_state)<br>
[`health_status`](#health_status)<br>
[`body_imaging`](#body_imaging)<br>
</details>

<details><summary>Medical Procedure</summary>

[`organ_condition`](#organ_condition)<br>
[`procedure_date`](#procedure_date)<br>
[`perfusion_solution`](#perfusion_solution)<br>
[`pathologist_report`](#pathologist_report)<br>
[`warm_ischemia_time_value`](#warm_ischemia_time_value)<br>
[`warm_ischemia_time_unit`](#warm_ischemia_time_unit)<br>
[`cold_ischemia_time_value`](#cold_ischemia_time_value)<br>
[`cold_ischemia_time_unit`](#cold_ischemia_time_unit)<br>
</details>

<details><summary>Biospecimen</summary>

[`specimen_preservation_temperature`](#specimen_preservation_temperature)<br>
[`specimen_quality_criteria`](#specimen_quality_criteria)<br>
[`biospecimen_selection_distance_from_tumor_value`](#biospecimen_selection_distance_from_tumor_value)<br></details>

## IDs

### `sample_id`
TODO

| constraint | value |
| --- | --- |
| required | `True` |
| pattern (regular expression) | `([A-Z]+[0-9]+)-(BL\|BR\|LB\|RB\|HT\|LK\|RK\|LI\|LV\|LL\|RL\|LY\d\d\|SI\|SP\|TH\|TR\|UR\|OT)(-\d+)+(_\d+)?` |

## Donor

### `vital_state`
Identify the vital state of the donor.

| constraint | value |
| --- | --- |
| required | `True` |
| enum | `living` or `deceased` |

### `health_status`
Patient's physical condition immediately preceding death.

| constraint | value |
| --- | --- |
| required | `True` |
| enum | `cancer`, `relatively healthy`, or `chronic illness` |

### `body_imaging`
TODO. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |

## Medical Procedure

### `organ_condition`
TODO

| constraint | value |
| --- | --- |
| required | `True` |
| enum | `healthy` or `diseased` |

### `procedure_date`
TODO

| constraint | value |
| --- | --- |
| type | `date` |
| format | `%Y-%m-%d` |
| required | `True` |

### `perfusion_solution`
TODO

| constraint | value |
| --- | --- |
| required | `True` |
| enum | `UWS`, `HTK`, `Unknown`, or `None` |

### `pathologist_report`
Further details on organ level QC checks.

| constraint | value |
| --- | --- |
| required | `True` |

### `warm_ischemia_time_value`
donor asystole or cross-clamp to ice; for surgical specimens, time from devascularization of tissue to ice. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `False` |

### `warm_ischemia_time_unit`
Time unit

| constraint | value |
| --- | --- |
| required | `True` |
| enum | `minutes` |

### `cold_ischemia_time_value`
TODO. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `False` |

### `cold_ischemia_time_unit`
Time unit

| constraint | value |
| --- | --- |
| required | `True` |
| enum | `minutes` |

## Biospecimen

### `specimen_preservation_temperature`
The temperature of the medium during the preservation process.

| constraint | value |
| --- | --- |
| required | `True` |
| enum | `-196 Celsius`, `-80 Celsius`, `-20 Celsius`, or `Room Temperature` |

### `specimen_quality_criteria`
For example, RIN: 8.7. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |

### `biospecimen_selection_distance_from_tumor_value`
If surgical sample, how far from the tumor was the sample obtained from. Typically a number of centimeters, but Unknown is also accepted. Leave blank if not applicable. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |
| pattern (regular expression) | `\d+(\.\d+)? cm\|Unknown` |
