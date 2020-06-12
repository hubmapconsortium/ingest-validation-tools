# sample

Related files:
- [🔬 Background doc](TODO): More details about this type.
- [📝 TSV template](https://raw.githubusercontent.com/hubmapconsortium/ingest-validation-tools/master/docs/sample/sample-metadata.tsv): Use this to submit metadata.
- [💻 Source code](https://github.com/hubmapconsortium/ingest-validation-tools/edit/master/src/ingest_validation_tools/table-schemas/level-2/sample.yaml): Make a PR if this doc should be updated.

## Table of contents
<details><summary>IDs</summary>

[`donor_id`](#donor_id)<br>
[`sample_id`](#sample_id)<br>
</details>

<details><summary>Donor</summary>

[`donor_source_institution`](#donor_source_institution)<br>
[`donor_vital_state`](#donor_vital_state)<br>
[`donor_health_status`](#donor_health_status)<br>
</details>

<details><summary>Medical Procedure</summary>

[`medical_procedure_organ_condition`](#medical_procedure_organ_condition)<br>
[`medical_procedure_organ_id`](#medical_procedure_organ_id)<br>
[`medical_procedure_date_undertaken`](#medical_procedure_date_undertaken)<br>
[`medical_procedure_protocols`](#medical_procedure_protocols)<br>
[`medical_procedure_organ_perfusion_solution_type`](#medical_procedure_organ_perfusion_solution_type)<br>
[`medical_procedure_organ_qc_pathologist_report`](#medical_procedure_organ_qc_pathologist_report)<br>
[`medical_procedure_organ_transport_warm_ischemia_time_value`](#medical_procedure_organ_transport_warm_ischemia_time_value)<br>
[`medical_procedure_organ_transport_warm_ischemia_time_unit`](#medical_procedure_organ_transport_warm_ischemia_time_unit)<br>
[`medical_procedure_organ_transport_cold_ischemia_time_value`](#medical_procedure_organ_transport_cold_ischemia_time_value)<br>
[`medical_procedure_organ_transport_cold_ischemia_time_unit`](#medical_procedure_organ_transport_cold_ischemia_time_unit)<br>
</details>

<details><summary>Biospecimen</summary>

[`biospecimen_aliquot_mechanism_of_stabilization`](#biospecimen_aliquot_mechanism_of_stabilization)<br>
[`biospecimen_aliquot_long_term_preservative_type`](#biospecimen_aliquot_long_term_preservative_type)<br>
[`biospecimen_aliquot_temperature_in_preservation_solution_value`](#biospecimen_aliquot_temperature_in_preservation_solution_value)<br>
[`biospecimen_aliquot_temperature_in_preservation_solution_unit`](#biospecimen_aliquot_temperature_in_preservation_solution_unit)<br>
[`biospecimen_selection_qa_qc_measure_criteria_institution`](#biospecimen_selection_qa_qc_measure_criteria_institution)<br>
[`biospecimen_selection_distance_from_tumor_value`](#biospecimen_selection_distance_from_tumor_value)<br>
[`biospecimen_selection_distance_from_tumor_unit`](#biospecimen_selection_distance_from_tumor_unit)<br></details>

## IDs

### `donor_id`
TODO

| constraint | value |
| --- | --- |
| required | `True` |
| pattern (regular expression) | `[A-Z]+[0-9]+` |

### `sample_id`
TODO

| constraint | value |
| --- | --- |
| required | `True` |
| pattern (regular expression) | `([A-Z]+[0-9]+)-(BL\|BR\|LB\|RB\|HT\|LK\|RK\|LI\|LV\|LL\|RL\|LY\d\d\|SI\|SP\|TH\|TR\|UR\|OT)(-\d+)+(_\d+)?` |

## Donor

### `donor_source_institution`
Name of institution that sourced the donor (anonymized) - TODO - This could be trivially de-anonymized. Is this for this release, or something in the future?

| constraint | value |
| --- | --- |
| required | `True` |
| enum | `A`, `B`, or `C` |

### `donor_vital_state`
identify the vital state of the donor

| constraint | value |
| --- | --- |
| required | `True` |
| enum | `living` or `deceased` |

### `donor_health_status`
Patient's physical condition immediately preceding death. TODO - Confirm that you want precisely these three mutually exclusive values? I thought HuBMAP included only healthy tissue?

| constraint | value |
| --- | --- |
| required | `True` |
| enum | `cancer`, `relatively healthy`, or `chronic illness` |

## Medical Procedure

### `medical_procedure_organ_condition`
TODO

| constraint | value |
| --- | --- |
| required | `True` |
| enum | `healthy` or `diseased` |

### `medical_procedure_organ_id`
TODO - format? description?

| constraint | value |
| --- | --- |
| required | `True` |

### `medical_procedure_date_undertaken`
need to be filled out only if UNET data no available (e.g. live donor). Internal value, not public, optional only for donors without unet info  - TODO - What does "recentered" mean? We have no machinery for keeping some fields private... Should this not be included then. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| type | `date` |
| format | `%Y-%m-%d` |
| required | `False` |

### `medical_procedure_protocols`
protocols.io link that specifies medical/surgical procedure to obtain organ from deceased donors or surgical excision - TODO - Require protocols.io DOI?

| constraint | value |
| --- | --- |
| required | `True` |

### `medical_procedure_organ_perfusion_solution_type`
TODO

| constraint | value |
| --- | --- |
| required | `True` |
| enum | `UW solution`, `Celsior`, or `HTK` |

### `medical_procedure_organ_qc_pathologist_report`
Further details on organ level QC checks - TODO - This is the actual text of the pathology report? Do new-lines need to be preserved?

| constraint | value |
| --- | --- |
| required | `True` |

### `medical_procedure_organ_transport_warm_ischemia_time_value`
donor asystole or cross-clamp to ice; for surgical specimens, time from devascularization of tissue to ice.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

### `medical_procedure_organ_transport_warm_ischemia_time_unit`
Time unit

| constraint | value |
| --- | --- |
| required | `True` |
| enum | `minutes` |

### `medical_procedure_organ_transport_cold_ischemia_time_value`
TODO

| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

### `medical_procedure_organ_transport_cold_ischemia_time_unit`
Time unit

| constraint | value |
| --- | --- |
| required | `True` |
| enum | `minutes` |

## Biospecimen

### `biospecimen_aliquot_mechanism_of_stabilization`
The process by which biospecimens were stabilized during collection. TODO - Does "none" mean unknown, or that there was no stabilization? Should protocols.io be referenced?

| constraint | value |
| --- | --- |
| required | `True` |
| enum | `snap freezing`, `controlled-rate freezing`, `dry ice freezing`, `ethanol-dry ice freezing`, `liquid nitrogen freezing`, `dry ice isopentane freezing`, `flash freezing`, `neutral buffered formalin`, `paraformaldehyde`, `dry ice freezing in OCT`, or `none` |

### `biospecimen_aliquot_long_term_preservative_type`
The final medium in which sample is placed. TODO - Are these the precise values you want? Do you also want to reference a protocol? Does "none" mean there is no long-term preservation? or that it's unknown? FFPE moved here as Sanjay requested. Confirm that this is correct?

| constraint | value |
| --- | --- |
| required | `True` |
| enum | `Alcohol-based (ETH)`, `Aldehyde-based (ALD)`, `Allprotect tissue reagent (ALL)`, `Heat stabilization (HST)`, `Neutral buffered formalin (NBF)`, `Non-aldehyde based without acetic acid (NAA)`, `Non-aldehyde with acetic acid (ACA)`, `Non-buffered formalin (FOR)`, `Optimum cutting temperature medium (OCT)`, `Cryopreserved in sucrose-OCT`, `Other (ZZZ)`, `PAXgene tissue (PXT)`, `RNA Later (RNL)`, `Snap freezing (SNP)`, `CryoStor`, `10% serum-DMSO culture media`, `UW solution`, `4% PFA`, `MeOH`, `Liquid Nitrogen (LN)`, `CMC`, `dry ice-isopentane`, `Unknown (XXX)`, `FFPE`, or `none` |

### `biospecimen_aliquot_temperature_in_preservation_solution_value`
The temperature of the medium during the preservation process. TODO - What does the protocol.io mean here?

| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

### `biospecimen_aliquot_temperature_in_preservation_solution_unit`
Temperature unit

| constraint | value |
| --- | --- |
| required | `True` |
| enum | `Celsius` |

### `biospecimen_selection_qa_qc_measure_criteria_institution`
For example, RIN: 8.7. TODO - What is the source_site,receiving_assay_site? Two fields? Any format constraint possible. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |

### `biospecimen_selection_distance_from_tumor_value`
If surgical sample, how far from the tumor was the sample obtained from. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `False` |

### `biospecimen_selection_distance_from_tumor_unit`
Units for distance from tumor. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |
| enum | `cm` |
