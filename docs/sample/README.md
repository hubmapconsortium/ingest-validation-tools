# sample

Related files:
- [🔬 Background doc](TODO): More details about this type.
- [📝 TSV template](https://raw.githubusercontent.com/hubmapconsortium/ingest-validation-tools/master/docs/sample/sample-metadata.tsv): Use this to submit metadata.
- [💻 Source code](https://github.com/hubmapconsortium/ingest-validation-tools/edit/master/src/ingest_validation_tools/table-schemas/level-2/sample.yaml): Make a PR if this doc should be updated.

## Table of contents
[`donor.source.institution`](#donor.source.institution)<br>
[`donor.vital_state`](#donor.vital_state)<br>
[`donor.health_status`](#donor.health_status)<br>
[`medical_procedure.organ.condition`](#medical_procedure.organ.condition)<br>
[`medical_procedure.organ.id`](#medical_procedure.organ.id)<br>
[`medical_procedure.date_undertaken`](#medical_procedure.date_undertaken)<br>
[`medical_procedure.protocols`](#medical_procedure.protocols)<br>
[`medical_procedure.organ_perfusion.solution_type`](#medical_procedure.organ_perfusion.solution_type)<br>
[`medical_procedure.organ.qc.pathologist_report`](#medical_procedure.organ.qc.pathologist_report)<br>
[`medical_procedure.organ.transport.warm_ischemia_time`](#medical_procedure.organ.transport.warm_ischemia_time)<br>
[`medical_procedure.organ.transport.cold_ischemia_time`](#medical_procedure.organ.transport.cold_ischemia_time)<br>
[`biospecimen_aliquot.mechanism_of_stabilization`](#biospecimen_aliquot.mechanism_of_stabilization)<br>
[`biospecimen_aliquot.long_term_preservative.type`](#biospecimen_aliquot.long_term_preservative.type)<br>
[`biospecimen_aliquot.temperature_in_preservation_solution`](#biospecimen_aliquot.temperature_in_preservation_solution)<br>
[`biospecimen_selection.qa_qc_measure_criteria.institution`](#biospecimen_selection.qa_qc_measure_criteria.institution)<br>
[`biospecimen_selection.distance_from_tumor`](#biospecimen_selection.distance_from_tumor)<br></details>

### `donor.source.institution`
Name of institution that sourced the donor (anonymized) - TODO - This could be trivially de-anonymized. Is this for this release, or something in the future?

| constraint | value |
| --- | --- |
| required | `True` |
| enum | `A`, `B`, or `C` |

### `donor.vital_state`
identify the vital state of the donor

| constraint | value |
| --- | --- |
| required | `True` |
| enum | `Live` or `Deceased` |

### `donor.health_status`
Patient's physical condition immediately preceding death. TODO - Confirm that you want precisely these three mutually exclusive values? I thought HuBMAP included only healthy tissue?

| constraint | value |
| --- | --- |
| required | `True` |
| enum | `cancer`, `relatively healthy`, or `chronic illness` |

### `medical_procedure.organ.condition`
TODO

| constraint | value |
| --- | --- |
| required | `True` |
| enum | `healthy` or `diseased` |

### `medical_procedure.organ.id`
TODO - format? description?

| constraint | value |
| --- | --- |
| required | `True` |

### `medical_procedure.date_undertaken`
need to be filled out only if UNET data no available (e.g. live donor). Internal value, not public, optional only for donors without unet info  - TODO - What does "recentered" mean? We have no machinery for keeping some fields private... Should this not be included then. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| type | `date` |
| format | `%Y-%m-%d` |
| required | `False` |

### `medical_procedure.protocols`
protocols.io link that specifies medical/surgical procedure to obtain organ from deceased donors or surgical excision - TODO - Require protocols.io DOI?

| constraint | value |
| --- | --- |
| required | `True` |

### `medical_procedure.organ_perfusion.solution_type`
TODO

| constraint | value |
| --- | --- |
| required | `True` |
| enum | `UW solution`, `Celsior`, or `HTK` |

### `medical_procedure.organ.qc.pathologist_report`
Further details on organ level QC checks - TODO - This is the actual text of the pathology report? Do new-lines need to be preserved?

| constraint | value |
| --- | --- |
| required | `True` |

### `medical_procedure.organ.transport.warm_ischemia_time`
donor asystole or cross-clamp to ice; for surgical specimens, time from devascularization of tissue to ice. TODO- Units somewhere.

| constraint | value |
| --- | --- |
| required | `True` |

### `medical_procedure.organ.transport.cold_ischemia_time`
min - TODO - Chuck really encourages either a separate units column or units in field name.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

### `biospecimen_aliquot.mechanism_of_stabilization`
The process by which biospecimens were stabilized during collection. TODO - Does "none" mean unknown, or that there was no stabilization? Should protocols.io be referenced?

| constraint | value |
| --- | --- |
| required | `True` |
| enum | `snap freezing`, `controlled-rate freezing`, `dry ice freezing`, `ethanol-dry ice freezing`, `liquid nitrogen freezing`, `dry ice isopentane freezing`, `flash freezing`, `neutral buffered formalin`, `paraformaldehyde`, `dry ice freezing in OCT`, or `none` |

### `biospecimen_aliquot.long_term_preservative.type`
The final medium in which sample is placed. TODO - Are these the precise values you want? Do you also want to reference a protocol? Does "none" mean there is no long-term preservation? or that it's unknown? FFPE moved here as Sanjay requested. Confirm that this is correct?

| constraint | value |
| --- | --- |
| required | `True` |
| enum | `Alcohol-based (ETH)`, `Aldehyde-based (ALD)`, `Allprotect tissue reagent (ALL)`, `Heat stabilization (HST)`, `Neutral buffered formalin (NBF)`, `Non-aldehyde based without acetic acid (NAA)`, `Non-aldehyde with acetic acid (ACA)`, `Non-buffered formalin (FOR)`, `Optimum cutting temperature medium (OCT)`, `Cryopreserved in sucrose-OCT`, `Other (ZZZ)`, `PAXgene tissue (PXT)`, `RNA Later (RNL)`, `Snap freezing (SNP)`, `CryoStor`, `10% serum-DMSO culture media`, `UW solution`, `4% PFA`, `MeOH`, `Liquid Nitrogen (LN)`, `CMC`, `dry ice-isopentane`, `Unknown (XXX)`, `FFPE`, or `none` |

### `biospecimen_aliquot.temperature_in_preservation_solution`
The temperature of the medium during the preservation process. TODO - Suggest unit in column name or separate column. - What does the protocol.io mean here?

| constraint | value |
| --- | --- |
| required | `True` |

### `biospecimen_selection.qa_qc_measure_criteria.institution`
For example, RIN: 8.7. TODO - What is the source_site,receiving_assay_site? Two fields? Any format constraint possible. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |

### `biospecimen_selection.distance_from_tumor`
If surgical sample, how far from the tumor was the sample obtained from. TODO - Suggest either including unit in name or as separate column. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `False` |
