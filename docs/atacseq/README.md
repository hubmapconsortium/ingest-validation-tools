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
[`is_technical_replicate`](#is_technical_replicate)<br>
[`library_id`](#library_id)<br>
[`sc_isolation_protocols_io_doi`](#sc_isolation_protocols_io_doi)<br>
[`sc_isolation_entity`](#sc_isolation_entity)<br>
[`sc_isolation_tissue_dissociation`](#sc_isolation_tissue_dissociation)<br>
[`sc_isolation_enrichment`](#sc_isolation_enrichment)<br>
[`sc_isolation_quality_metric`](#sc_isolation_quality_metric)<br>
[`sc_isolation_cell_number`](#sc_isolation_cell_number)<br>
[`transposition_input`](#transposition_input)<br>
[`transposition_method`](#transposition_method)<br>
[`transposition_transposase_source`](#transposition_transposase_source)<br>
[`transposition_kit_number`](#transposition_kit_number)<br>
[`library_construction_protocols_io_doi`](#library_construction_protocols_io_doi)<br>
[`library_layout`](#library_layout)<br>
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
[`sequencing_phix_percent`](#sequencing_phix_percent)<br>

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
DOI for protocols.io referring to the protocol for this assay.

| constraint | value |
| --- | --- |
| pattern | `^10\.17504/.*` |

### `operator`
Name of the person responsible for executing the assay.



### `operator_email`
Email address for the operator.

| constraint | value |
| --- | --- |
| format | `email` |

### `pi`
Name of the principal investigator responsible for the data.



### `pi_email`
Email address for the principal investigator.

| constraint | value |
| --- | --- |
| format | `email` |

### `assay_category`
Each assay is placed into one of the following 3 general categories: generation of images of microscopic entities, identification & quantitation of molecules by mass spectrometry, and determination of nucleotide sequence. TODO: Should this be an enumeration? What exact values?



### `assay_type`
The specific type of assay being executed.



### `analyte_class`
Analytes are the target molecules being measured with the assay.



### `is_targeted`
This is a boolean value that specifies whether or not a specific molecule(s) is/are targeted for detection/measurement by the assay. The CODEX analyte is protein. TODO: Should this be updated? Seems like copy and paste from CODEX.

| constraint | value |
| --- | --- |
| type | `boolean` |

## Level 2

### `acquisition_instrument_vendor`
An acquisition_instrument is the device that contains the signal detection hardware and signal processing software. Assays can generate signals such as light of various intensities or color or signals representing molecular mass.



### `acquisition_instrument_model`
Manufacturers of an acquisition instrument may offer various versions (models) of that instrument with different features or sensitivities. Differences in features or sensitivities may be relevant to processing or interpretation of the data.



### `is_technical_replicate`
If TRUE, fastq files in dataset need to be merged.

| constraint | value |
| --- | --- |
| type | `boolean` |

### `library_id`
A library ID, unique within a TMC, which allows corresponding RNA and chromatin accessibility datasets to be linked.



### `sc_isolation_protocols_io_doi`
Link to a protocols document answering the question: How were single cells separated into a single-cell suspension?

| constraint | value |
| --- | --- |
| pattern | `^10\.17504/.*` |

### `sc_isolation_entity`
The type of single cell entity derived from isolation protocol.

| constraint | value |
| --- | --- |
| enum | `['whole cell', 'nucleus', 'cell-cell multimer', 'spatially encoded cell barcoding']` |

### `sc_isolation_tissue_dissociation`
The method by which tissues are dissociated into single cells in suspension.



### `sc_isolation_enrichment`
The method by which specific cell populations are sorted or enriched.

| constraint | value |
| --- | --- |
| enum | `['none', 'FACS']` |

### `sc_isolation_quality_metric`
A quality metric by visual inspection prior to cell lysis or defined by known parameters such as wells with several cells or no cells. This can be captured at a high level. "OK" or "not OK", or with more specificity such as "debris", "clump", "low clump".



### `sc_isolation_cell_number`
Total number of cell/nuclei yielded post dissociation and enrichment.

| constraint | value |
| --- | --- |
| type | `number` |

### `transposition_input`
Number of cell/nuclei input to the assay.

| constraint | value |
| --- | --- |
| type | `number` |

### `transposition_method`
Modality of capturing accessible chromatin molecules.

| constraint | value |
| --- | --- |
| enum | `['SNARE-Seq2-AC', 'scATACseq', 'BulkATACseq', 'snATACseq', 'sciATACseq']` |

### `transposition_transposase_source`
The source of the Tn5 transposase and transposon used for capturing accessible chromatin. TODO- Is this an enum, or just examples?

| constraint | value |
| --- | --- |
| enum | `['10X snATAC', 'In-house', 'Nextera']` |

### `transposition_kit_number`
If Tn5 came from a kit, provide the catalog number.



### `library_construction_protocols_io_doi`
A link to the protocol document containing the library construction method (including version) that was used, e.g. "Smart-Seq2", "Drop-Seq", "10X v3". DOI for protocols.io referring to the protocol for this assay.

| constraint | value |
| --- | --- |
| pattern | `^10\.17504/.*` |

### `library_layout`
Whether the library was generated for single-end or paired end sequencing.

| constraint | value |
| --- | --- |
| enum | `['single-end', 'paired-end']` |

### `library_adapter_sequence`
Adapter sequence to be used for adapter trimming.



### `cell_barcode_read`
Which read file contains the cell barcode.

| constraint | value |
| --- | --- |
| enum | `['R1', 'R2', 'R3']` |

### `cell_barcode_offset`
Position in the read at which the cell barcode starts (if a single position). Does not apply to SNARE-seq and BulkATAC. Numeric value in bp.

| constraint | value |
| --- | --- |
| type | `number` |

### `cell_barcode_size`
Length of the cell barcode in base pairs. Does not apply to SNARE-seq and BulkATAC. Numeric value in bp

| constraint | value |
| --- | --- |
| type | `number` |

### `library_pcr_cycles`
Number of PCR cycles to enrich for accessible chromatin fragments.

| constraint | value |
| --- | --- |
| type | `number` |

### `library_pcr_cycles_for_sample_index`
Number of PCR cycles performed for library generation (figure in Descriptions section)

| constraint | value |
| --- | --- |
| type | `number` |

### `library_final_yield`
Total ng of library after final pcr amplification step. Numeric value in ng.

| constraint | value |
| --- | --- |
| type | `number` |

### `library_average_fragment_size`
Average size of sequencing library fragments estimated via gel electrophoresis or bioanalyzer/tapestation. Numeric value in bp.

| constraint | value |
| --- | --- |
| type | `number` |

### `sequencing_reagent_kit`
Reagent kit used for sequencing. NovaSeq6000 for example



### `sequencing_read_format`
Number of sequencing cycles in Read1, i7 index, i5 index, and Read2. Eg: for 10X snATAC-seq: 50+8+16+50 (R1,Index,R2,R3). For SNARE-seq2: 75+94+8+75



### `sequencing_read_percent_q30`
Percent of bases with Quality scores above Q30.

| constraint | value |
| --- | --- |
| type | `number` |

### `sequencing_phix_percent`
Percent PhiX loaded to the run.

| constraint | value |
| --- | --- |
| type | `number` |

