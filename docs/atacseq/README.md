# atacseq

Related files:
- [JSON Schema](schema.yaml)
- [TSV Template](template.tsv)

## Table of contents
[Provenance](#provenance)<br>
[`donor_id`](#donor_id)<br>
[`parent_id`](#parent_id)<br>
[Level 1](#level-1)<br>
[`execution_datetime`](#execution_datetime)<br>
[`sequencing_protocols_io_doi`](#sequencing_protocols_io_doi)<br>
[`operator`](#operator)<br>
[`operator_email`](#operator_email)<br>
[`pi`](#pi)<br>
[`pi_email`](#pi_email)<br>
[`assay_category`](#assay_category)<br>
[`assay_type`](#assay_type)<br>
[`analyte_class`](#analyte_class)<br>
[`is_targeted`](#is_targeted)<br>
[Level 2](#level-2)<br>
[`acquisition_instrument_vendor`](#acquisition_instrument_vendor)<br>
[`acquisition_instrument_model`](#acquisition_instrument_model)<br>
[`subspecimen_assay_input_number`](#subspecimen_assay_input_number)<br>
[`replicate_group_type`](#replicate_group_type)<br>
[`replicate_group_id`](#replicate_group_id)<br>
[`sc_isolation_protocols_io_doi`](#sc_isolation_protocols_io_doi)<br>
[`sc_isolation_entity`](#sc_isolation_entity)<br>
[`sc_isolation_tissue_dissociation`](#sc_isolation_tissue_dissociation)<br>
[`sc_isolation_enrichment`](#sc_isolation_enrichment)<br>
[`sc_isolation_quality_metric`](#sc_isolation_quality_metric)<br>
[`sc_isolation_cell_number`](#sc_isolation_cell_number)<br>
[`Transposition_input`](#transposition_input)<br>
[`Transposition_method`](#transposition_method)<br>
[`transposition_transposase_source`](#transposition_transposase_source)<br>
[`transposition_kit_number`](#transposition_kit_number)<br>
[`library_construction_protocols_io_doi`](#library_construction_protocols_io_doi)<br>
[`Library_layout`](#library_layout)<br>
[`library_adapter_sequence`](#library_adapter_sequence)<br>
[`cell_barcode_read`](#cell_barcode_read)<br>
[`cell_barcode_offset`](#cell_barcode_offset)<br>
[`cell_barcode_size`](#cell_barcode_size)<br>
[`library_pcr_cycles`](#library_pcr_cycles)<br>
[`library_pcr_cycles_for_sample_index`](#library_pcr_cycles_for_sample_index)<br>
[`library_final_yield`](#library_final_yield)<br>
[`library_average_fragment_size`](#library_average_fragment_size)<br>
[`sequencing_reagent_kit`](#sequencing_reagent_kit)<br>
[`sequencing_read_format`](#sequencing_read_format)<br>
[`sequencing_read_percent_q30`](#sequencing_read_percent_q30)<br>
[`sequencing_phiX_percent`](#sequencing_phix_percent)<br>

## Provenance

### `donor_id`
HuBMAP ID of the donor of the assayed tissue.

| constraint | value |
| --- | --- |
| format | `uuid` |

### `parent_id`
HuBMAP ID of the assayed tissue.

| constraint | value |
| --- | --- |
| format | `uuid` |

## Level 1

### `execution_datetime`
Start date and time of assay. YYYY-MM-DD hh:mm +/-hh:mm, where YYYY is the year, MM is the month with leading 0s, and DD is the day with leading 0s, hh is the hour with leading zeros, mm are the minutes with leading zeros, followed by the offset from GMT.

| constraint | value |
| --- | --- |
| type | `datetime` |
| format | `%Y-%m-%d %H:%M %z` |

### `sequencing_protocols_io_doi`
None



### `operator`
None



### `operator_email`
None

| constraint | value |
| --- | --- |
| format | `email` |

### `pi`
None



### `pi_email`
None

| constraint | value |
| --- | --- |
| format | `email` |

### `assay_category`
None



### `assay_type`
None



### `analyte_class`
None



### `is_targeted`
None

| constraint | value |
| --- | --- |
| type | `boolean` |

## Level 2

### `acquisition_instrument_vendor`
None



### `acquisition_instrument_model`
None



### `subspecimen_assay_input_number`
Numeric value in mg; TODO- Field name does't seem right?

| constraint | value |
| --- | --- |
| type | `number` |

### `replicate_group_type`
If present, indicates that this is a replicate of the dataset sharing the same replicate_group_id, but with no replicate_group_type.

| constraint | value |
| --- | --- |
| enum | `['biological', 'technical', 'multimodal']` |

### `replicate_group_id`
an alpha-numeric group name



### `sc_isolation_protocols_io_doi`
DOI for protocols.io referring to the protocol for this assay



### `sc_isolation_entity`
None

| constraint | value |
| --- | --- |
| enum | `['whole cell', 'nucleus', 'cell-cell multimer', 'spatially encoded cell barcoding']` |

### `sc_isolation_tissue_dissociation`
Examples are "proteolysis", "mesh passage", "fine needle trituration", dounce



### `sc_isolation_enrichment`
None

| constraint | value |
| --- | --- |
| enum | `['none', 'FACS']` |

### `sc_isolation_quality_metric`
"OK" or "not OK", or with more specificity such as "debris", "clump", "low clump".



### `sc_isolation_cell_number`
None

| constraint | value |
| --- | --- |
| type | `number` |

### `Transposition_input`
None

| constraint | value |
| --- | --- |
| type | `number` |

### `Transposition_method`
None

| constraint | value |
| --- | --- |
| enum | `['SNARE-Seq2-AC', 'scATACseq', 'BulkATACseq', 'snATACseq', 'sciATACseq']` |

### `transposition_transposase_source`
TODO- Is this an enum, or just examples?

| constraint | value |
| --- | --- |
| enum | `['10X snATAC', 'In-house produced (Protocol Reference)', 'Nextera']` |

### `transposition_kit_number`
None



### `library_construction_protocols_io_doi`
DOI for protocols.io referring to the protocol for this assay



### `Library_layout`
None

| constraint | value |
| --- | --- |
| enum | `['single-end', 'paired-end']` |

### `library_adapter_sequence`
None



### `cell_barcode_read`
None

| constraint | value |
| --- | --- |
| enum | `['R1', 'R2', 'R3']` |

### `cell_barcode_offset`
Numeric value in bp

| constraint | value |
| --- | --- |
| type | `number` |

### `cell_barcode_size`
Numeric value in bp

| constraint | value |
| --- | --- |
| type | `number` |

### `library_pcr_cycles`
None

| constraint | value |
| --- | --- |
| type | `number` |

### `library_pcr_cycles_for_sample_index`
None

| constraint | value |
| --- | --- |
| type | `number` |

### `library_final_yield`
Numeric value in ng.

| constraint | value |
| --- | --- |
| type | `number` |

### `library_average_fragment_size`
Numeric value in bp.

| constraint | value |
| --- | --- |
| type | `number` |

### `sequencing_reagent_kit`
NovaSeq6000 for example



### `sequencing_read_format`
Eg: for 10X snATAC-seq: 50+8+16+50 (R1,Index,R2,R3). For SNARE-seq2: 75+94+8+75



### `sequencing_read_percent_q30`
[0-1]; TODO- This is not a percentage. Change the name or change the value?

| constraint | value |
| --- | --- |
| type | `number` |

### `sequencing_phiX_percent`
[0-1]; TODO- This is not a percentage.

| constraint | value |
| --- | --- |
| type | `number` |

