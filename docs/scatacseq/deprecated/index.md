---
title: SNARE-seq2 / sciATACseq / snATACseq
schema_name: scatacseq
category: Sequence Assays
all_versions_deprecated: False
exclude_from_index: False
layout: default
permalink: /scatacseq/
---

Related files:
- [🔬 Background doc](https://portal.hubmapconsortium.org/docs/assays/atacseq): More details about this type.

- [📝 Excel template](https://raw.githubusercontent.com/hubmapconsortium/ingest-validation-tools/main/docs/scatacseq/deprecated/scatacseq-metadata.xlsx): For metadata entry.
- [📝 TSV template](https://raw.githubusercontent.com/hubmapconsortium/ingest-validation-tools/main/docs/scatacseq/deprecated/scatacseq-metadata.tsv): Alternative for metadata entry.


This schema is for the single nucleus Assay for Transposase Accessible Chromatin by sequencing (snATACseq).

## Metadata schema


<details markdown="1" open="true"><summary><b>Version 1 (use this one)</b></summary>

<blockquote markdown="1">

<details markdown="1"><summary>Shared by all types</summary>

[`version`](#version)<br>
[`description`](#description)<br>
[`donor_id`](#donor_id)<br>
[`tissue_id`](#tissue_id)<br>
[`execution_datetime`](#execution_datetime)<br>
[`protocols_io_doi`](#protocols_io_doi)<br>
[`operator`](#operator)<br>
[`operator_email`](#operator_email)<br>
[`pi`](#pi)<br>
[`pi_email`](#pi_email)<br>
[`assay_category`](#assay_category)<br>
[`assay_type`](#assay_type)<br>
[`analyte_class`](#analyte_class)<br>
[`is_targeted`](#is_targeted)<br>
[`acquisition_instrument_vendor`](#acquisition_instrument_vendor)<br>
[`acquisition_instrument_model`](#acquisition_instrument_model)<br>

</details>
<details markdown="1"><summary>Unique to this type</summary>

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
[`library_final_yield_unit`](#library_final_yield_unit)<br>
[`library_average_fragment_size`](#library_average_fragment_size)<br>
[`sequencing_reagent_kit`](#sequencing_reagent_kit)<br>
[`sequencing_read_format`](#sequencing_read_format)<br>
[`sequencing_read_percent_q30`](#sequencing_read_percent_q30)<br>
[`sequencing_phix_percent`](#sequencing_phix_percent)<br>
[`contributors_path`](#contributors_path)<br>
[`data_path`](#data_path)<br>
</details>

</blockquote>

### Shared by all types

<a name="version"></a>
##### [`version`](#version)
Version of the schema to use when validating this metadata.

| constraint | value |
| --- | --- |
| enum | `1` |
| required | `True` |

<a name="description"></a>
##### [`description`](#description)
Free-text description of this assay.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="donor_id"></a>
##### [`donor_id`](#donor_id)
HuBMAP Display ID of the donor of the assayed tissue. Example: `ABC123`.

| constraint | value |
| --- | --- |
| pattern (regular expression) | <code>[A-Z]+[0-9]+</code> |
| required | `True` |

<a name="tissue_id"></a>
##### [`tissue_id`](#tissue_id)
HuBMAP Display ID of the assayed tissue. Example: `ABC123-BL-1-2-3_456`.

| constraint | value |
| --- | --- |
| pattern (regular expression) | <code>(([A-Z]+[0-9]+)-[A-Z]{2}\d*(-\d+)+(_\d+)?)(,([A-Z]+[0-9]+)-[A-Z]{2}\d*(-\d+)+(_\d+)?)*</code> |
| required | `True` |

<a name="execution_datetime"></a>
##### [`execution_datetime`](#execution_datetime)
Start date and time of assay, typically a date-time stamped folder generated by the acquisition instrument. YYYY-MM-DD hh:mm, where YYYY is the year, MM is the month with leading 0s, and DD is the day with leading 0s, hh is the hour with leading zeros, mm are the minutes with leading zeros.

| constraint | value |
| --- | --- |
| type | `datetime` |
| format | `%Y-%m-%d %H:%M` |
| required | `True` |

<a name="protocols_io_doi"></a>
##### [`protocols_io_doi`](#protocols_io_doi)
DOI for protocols.io referring to the protocol for this assay.

| constraint | value |
| --- | --- |
| required | `True` |
| pattern (regular expression) | <code>10\.17504/.*</code> |
| url | prefix: <code>https://dx.doi.org/</code> |

<a name="operator"></a>
##### [`operator`](#operator)
Name of the person responsible for executing the assay.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="operator_email"></a>
##### [`operator_email`](#operator_email)
Email address for the operator.

| constraint | value |
| --- | --- |
| format | `email` |
| required | `True` |

<a name="pi"></a>
##### [`pi`](#pi)
Name of the principal investigator responsible for the data.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="pi_email"></a>
##### [`pi_email`](#pi_email)
Email address for the principal investigator.

| constraint | value |
| --- | --- |
| format | `email` |
| required | `True` |

<a name="assay_category"></a>
##### [`assay_category`](#assay_category)
Each assay is placed into one of the following 4 general categories: generation of images of microscopic entities, identification & quantitation of molecules by mass spectrometry, imaging mass spectrometry, and determination of nucleotide sequence.

| constraint | value |
| --- | --- |
| enum | `sequence` |
| required | `True` |

<a name="assay_type"></a>
##### [`assay_type`](#assay_type)
The specific type of assay being executed.

| constraint | value |
| --- | --- |
| enum | `SNARE-seq2`, `sciATACseq`, or `snATACseq` |
| required | `True` |

<a name="analyte_class"></a>
##### [`analyte_class`](#analyte_class)
Analytes are the target molecules being measured with the assay.

| constraint | value |
| --- | --- |
| enum | `DNA` |
| required | `True` |

<a name="is_targeted"></a>
##### [`is_targeted`](#is_targeted)
Specifies whether or not a specific molecule(s) is/are targeted for detection/measurement by the assay.

| constraint | value |
| --- | --- |
| type | `boolean` |
| required | `True` |

<a name="acquisition_instrument_vendor"></a>
##### [`acquisition_instrument_vendor`](#acquisition_instrument_vendor)
An acquisition instrument is the device that contains the signal detection hardware and signal processing software. Assays generate signals such as light of various intensities or color or signals representing the molecular mass.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="acquisition_instrument_model"></a>
##### [`acquisition_instrument_model`](#acquisition_instrument_model)
Manufacturers of an acquisition instrument may offer various versions (models) of that instrument with different features or sensitivities. Differences in features or sensitivities may be relevant to processing or interpretation of the data.

| constraint | value |
| --- | --- |
| required | `True` |

### Unique to this type

<a name="is_technical_replicate"></a>
##### [`is_technical_replicate`](#is_technical_replicate)
If TRUE, fastq files in dataset need to be merged.

| constraint | value |
| --- | --- |
| type | `boolean` |
| required | `True` |

<a name="library_id"></a>
##### [`library_id`](#library_id)
A library ID, unique within a TMC, which allows corresponding RNA and chromatin accessibility datasets to be linked.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="sc_isolation_protocols_io_doi"></a>
##### [`sc_isolation_protocols_io_doi`](#sc_isolation_protocols_io_doi)
Link to a protocols document answering the question: How were single cells separated into a single-cell suspension?

| constraint | value |
| --- | --- |
| required | `True` |
| pattern (regular expression) | <code>10\.17504/.*</code> |
| url | prefix: <code>https://dx.doi.org/</code> |

<a name="sc_isolation_entity"></a>
##### [`sc_isolation_entity`](#sc_isolation_entity)
The type of single cell entity derived from isolation protocol.

| constraint | value |
| --- | --- |
| enum | `whole cell`, `nucleus`, `cell-cell multimer`, or `spatially encoded cell barcoding` |
| required | `True` |

<a name="sc_isolation_tissue_dissociation"></a>
##### [`sc_isolation_tissue_dissociation`](#sc_isolation_tissue_dissociation)
The method by which tissues are dissociated into single cells in suspension.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="sc_isolation_enrichment"></a>
##### [`sc_isolation_enrichment`](#sc_isolation_enrichment)
The method by which specific cell populations are sorted or enriched.

| constraint | value |
| --- | --- |
| enum | `none` or `FACS` |
| required | `True` |

<a name="sc_isolation_quality_metric"></a>
##### [`sc_isolation_quality_metric`](#sc_isolation_quality_metric)
A quality metric by visual inspection prior to cell lysis or defined by known parameters such as wells with several cells or no cells. This can be captured at a high level. "OK" or "not OK", or with more specificity such as "debris", "clump", "low clump".

| constraint | value |
| --- | --- |
| required | `True` |

<a name="sc_isolation_cell_number"></a>
##### [`sc_isolation_cell_number`](#sc_isolation_cell_number)
Total number of cell/nuclei yielded post dissociation and enrichment.

| constraint | value |
| --- | --- |
| type | `integer` |
| required | `True` |

<a name="transposition_input"></a>
##### [`transposition_input`](#transposition_input)
Number of cell/nuclei input to the assay.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

<a name="transposition_method"></a>
##### [`transposition_method`](#transposition_method)
Modality of capturing accessible chromatin molecules.

| constraint | value |
| --- | --- |
| enum | `SNARE-Seq2-AC`, `bulkATACseq`, `snATACseq`, or `sciATACseq` |
| required | `True` |

<a name="transposition_transposase_source"></a>
##### [`transposition_transposase_source`](#transposition_transposase_source)
The source of the Tn5 transposase and transposon used for capturing accessible chromatin.

| constraint | value |
| --- | --- |
| enum | `10X snATAC`, `In-house`, `Nextera`, or `10X multiome` |
| required | `True` |

<a name="transposition_kit_number"></a>
##### [`transposition_kit_number`](#transposition_kit_number)
If Tn5 came from a kit, provide the catalog number. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |

<a name="library_construction_protocols_io_doi"></a>
##### [`library_construction_protocols_io_doi`](#library_construction_protocols_io_doi)
A link to the protocol document containing the library construction method (including version) that was used, e.g. "Smart-Seq2", "Drop-Seq", "10X v3". DOI for protocols.io referring to the protocol for this assay.

| constraint | value |
| --- | --- |
| required | `True` |
| pattern (regular expression) | <code>10\.17504/.*</code> |
| url | prefix: <code>https://dx.doi.org/</code> |

<a name="library_layout"></a>
##### [`library_layout`](#library_layout)
State whether the library was generated for single-end or paired end sequencing.

| constraint | value |
| --- | --- |
| enum | `single-end` or `paired-end` |
| required | `True` |

<a name="library_adapter_sequence"></a>
##### [`library_adapter_sequence`](#library_adapter_sequence)
Adapter sequence to be used for adapter trimming. Example: `CTGTCTCTTATACACATCT`.

| constraint | value |
| --- | --- |
| pattern (regular expression) | <code>[ATCG]+(\+[ATCG]+)?</code> |
| required | `True` |

<a name="cell_barcode_read"></a>
##### [`cell_barcode_read`](#cell_barcode_read)
Which read file(s) contains the cell barcode. Multiple cell_barcode_read files must be provided as a comma-delimited list (e.g. file1,file2,file3). This field is not required for barcoding by single-cell combinatorial indexing. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |

<a name="cell_barcode_offset"></a>
##### [`cell_barcode_offset`](#cell_barcode_offset)
Positions in the read at which the cell barcodes start. Cell barcodes are, for example, 3 x 8 bp sequences that are spaced by constant sequences (the offsets). First barcode at position 0, then 38, then 76. (Does not apply to sciATACseq, SNARE-seq and BulkATAC.) Leave blank if not applicable. Example: `0,0,38,76`.

| constraint | value |
| --- | --- |
| required | `False` |
| pattern (regular expression) | <code>\d+(,\d+)*</code> |

<a name="cell_barcode_size"></a>
##### [`cell_barcode_size`](#cell_barcode_size)
Length of the cell barcode in base pairs. Cell barcodes are, for example, 3 x 8 bp sequences that are spaced by constant sequences, the offsets. (Does not apply to sciATACseq, SNARE-seq and BulkATAC.) Leave blank if not applicable. Example: `16,8,8,8`.

| constraint | value |
| --- | --- |
| required | `False` |
| pattern (regular expression) | <code>\d+(,\d+)*</code> |

<a name="library_pcr_cycles"></a>
##### [`library_pcr_cycles`](#library_pcr_cycles)
Number of PCR cycles to enrich for accessible chromatin fragments.

| constraint | value |
| --- | --- |
| type | `integer` |
| required | `True` |

<a name="library_pcr_cycles_for_sample_index"></a>
##### [`library_pcr_cycles_for_sample_index`](#library_pcr_cycles_for_sample_index)
Number of PCR cycles performed for library generation (figure in Descriptions section)

| constraint | value |
| --- | --- |
| type | `integer` |
| required | `True` |

<a name="library_final_yield"></a>
##### [`library_final_yield`](#library_final_yield)
Total ng of library after final pcr amplification step.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

<a name="library_final_yield_unit"></a>
##### [`library_final_yield_unit`](#library_final_yield_unit)
Units for library_final_yield. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| enum | `ng` |
| required | `False` |
| required if | `library_final_yield` present |

<a name="library_average_fragment_size"></a>
##### [`library_average_fragment_size`](#library_average_fragment_size)
Average size in basepairs (bp) of sequencing library fragments estimated via gel electrophoresis or bioanalyzer/tapestation.

| constraint | value |
| --- | --- |
| type | `integer` |
| required | `True` |

<a name="sequencing_reagent_kit"></a>
##### [`sequencing_reagent_kit`](#sequencing_reagent_kit)
Reagent kit used for sequencing.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="sequencing_read_format"></a>
##### [`sequencing_read_format`](#sequencing_read_format)
Slash-delimited list of the number of sequencing cycles for, for example, Read1, i7 index, i5 index, and Read2. Example: `12/34/56`.

| constraint | value |
| --- | --- |
| pattern (regular expression) | <code>\d+(/\d+)+</code> |
| required | `True` |

<a name="sequencing_read_percent_q30"></a>
##### [`sequencing_read_percent_q30`](#sequencing_read_percent_q30)
Q30 is the weighted average of all the reads (e.g. # bases UMI * q30 UMI + # bases R2 * q30 R2 + ...)

| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |
| minimum | `0` |
| maximum | `100` |

<a name="sequencing_phix_percent"></a>
##### [`sequencing_phix_percent`](#sequencing_phix_percent)
Percent PhiX loaded to the run.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |
| minimum | `0` |
| maximum | `100` |

<a name="contributors_path"></a>
##### [`contributors_path`](#contributors_path)
Relative path to file with ORCID IDs for contributors for this dataset.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="data_path"></a>
##### [`data_path`](#data_path)
Relative path to file or directory with instrument data. Downstream processing will depend on filename extension conventions.

| constraint | value |
| --- | --- |
| required | `True` |

</details>


<details markdown="1" ><summary><b>Version 0</b></summary>


### Shared by all types

<a name="donor_id"></a>
##### [`donor_id`](#donor_id)
HuBMAP Display ID of the donor of the assayed tissue. Example: `ABC123`.

| constraint | value |
| --- | --- |
| pattern (regular expression) | <code>[A-Z]+[0-9]+</code> |
| required | `True` |

<a name="tissue_id"></a>
##### [`tissue_id`](#tissue_id)
HuBMAP Display ID of the assayed tissue. Example: `ABC123-BL-1-2-3_456`.

| constraint | value |
| --- | --- |
| pattern (regular expression) | <code>([A-Z]+[0-9]+)-[A-Z]{2}\d*(-\d+)+(_\d+)?</code> |
| required | `True` |

<a name="execution_datetime"></a>
##### [`execution_datetime`](#execution_datetime)
Start date and time of assay, typically a date-time stamped folder generated by the acquisition instrument. YYYY-MM-DD hh:mm, where YYYY is the year, MM is the month with leading 0s, and DD is the day with leading 0s, hh is the hour with leading zeros, mm are the minutes with leading zeros.

| constraint | value |
| --- | --- |
| type | `datetime` |
| format | `%Y-%m-%d %H:%M` |
| required | `True` |

<a name="protocols_io_doi"></a>
##### [`protocols_io_doi`](#protocols_io_doi)
DOI for protocols.io referring to the protocol for this assay.

| constraint | value |
| --- | --- |
| required | `True` |
| pattern (regular expression) | <code>10\.17504/.*</code> |
| url | prefix: <code>https://dx.doi.org/</code> |

<a name="operator"></a>
##### [`operator`](#operator)
Name of the person responsible for executing the assay.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="operator_email"></a>
##### [`operator_email`](#operator_email)
Email address for the operator.

| constraint | value |
| --- | --- |
| format | `email` |
| required | `True` |

<a name="pi"></a>
##### [`pi`](#pi)
Name of the principal investigator responsible for the data.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="pi_email"></a>
##### [`pi_email`](#pi_email)
Email address for the principal investigator.

| constraint | value |
| --- | --- |
| format | `email` |
| required | `True` |

<a name="assay_category"></a>
##### [`assay_category`](#assay_category)
Each assay is placed into one of the following 4 general categories: generation of images of microscopic entities, identification & quantitation of molecules by mass spectrometry, imaging mass spectrometry, and determination of nucleotide sequence.

| constraint | value |
| --- | --- |
| enum | `sequence` |
| required | `True` |

<a name="assay_type"></a>
##### [`assay_type`](#assay_type)
The specific type of assay being executed.

| constraint | value |
| --- | --- |
| enum | `SNARE-seq2`, `sciATACseq`, or `snATACseq` |
| required | `True` |

<a name="analyte_class"></a>
##### [`analyte_class`](#analyte_class)
Analytes are the target molecules being measured with the assay.

| constraint | value |
| --- | --- |
| enum | `DNA` |
| required | `True` |

<a name="is_targeted"></a>
##### [`is_targeted`](#is_targeted)
Specifies whether or not a specific molecule(s) is/are targeted for detection/measurement by the assay.

| constraint | value |
| --- | --- |
| type | `boolean` |
| required | `True` |

<a name="acquisition_instrument_vendor"></a>
##### [`acquisition_instrument_vendor`](#acquisition_instrument_vendor)
An acquisition instrument is the device that contains the signal detection hardware and signal processing software. Assays generate signals such as light of various intensities or color or signals representing the molecular mass.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="acquisition_instrument_model"></a>
##### [`acquisition_instrument_model`](#acquisition_instrument_model)
Manufacturers of an acquisition instrument may offer various versions (models) of that instrument with different features or sensitivities. Differences in features or sensitivities may be relevant to processing or interpretation of the data.

| constraint | value |
| --- | --- |
| required | `True` |

### Unique to this type

<a name="is_technical_replicate"></a>
##### [`is_technical_replicate`](#is_technical_replicate)
If TRUE, fastq files in dataset need to be merged.

| constraint | value |
| --- | --- |
| type | `boolean` |
| required | `True` |

<a name="library_id"></a>
##### [`library_id`](#library_id)
A library ID, unique within a TMC, which allows corresponding RNA and chromatin accessibility datasets to be linked.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="sc_isolation_protocols_io_doi"></a>
##### [`sc_isolation_protocols_io_doi`](#sc_isolation_protocols_io_doi)
Link to a protocols document answering the question: How were single cells separated into a single-cell suspension?

| constraint | value |
| --- | --- |
| required | `True` |
| pattern (regular expression) | <code>10\.17504/.*</code> |
| url | prefix: <code>https://dx.doi.org/</code> |

<a name="sc_isolation_entity"></a>
##### [`sc_isolation_entity`](#sc_isolation_entity)
The type of single cell entity derived from isolation protocol.

| constraint | value |
| --- | --- |
| enum | `whole cell`, `nucleus`, `cell-cell multimer`, or `spatially encoded cell barcoding` |
| required | `True` |

<a name="sc_isolation_tissue_dissociation"></a>
##### [`sc_isolation_tissue_dissociation`](#sc_isolation_tissue_dissociation)
The method by which tissues are dissociated into single cells in suspension.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="sc_isolation_enrichment"></a>
##### [`sc_isolation_enrichment`](#sc_isolation_enrichment)
The method by which specific cell populations are sorted or enriched.

| constraint | value |
| --- | --- |
| enum | `none` or `FACS` |
| required | `True` |

<a name="sc_isolation_quality_metric"></a>
##### [`sc_isolation_quality_metric`](#sc_isolation_quality_metric)
A quality metric by visual inspection prior to cell lysis or defined by known parameters such as wells with several cells or no cells. This can be captured at a high level. "OK" or "not OK", or with more specificity such as "debris", "clump", "low clump".

| constraint | value |
| --- | --- |
| required | `True` |

<a name="sc_isolation_cell_number"></a>
##### [`sc_isolation_cell_number`](#sc_isolation_cell_number)
Total number of cell/nuclei yielded post dissociation and enrichment.

| constraint | value |
| --- | --- |
| type | `integer` |
| required | `True` |

<a name="transposition_input"></a>
##### [`transposition_input`](#transposition_input)
Number of cell/nuclei input to the assay.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

<a name="transposition_method"></a>
##### [`transposition_method`](#transposition_method)
Modality of capturing accessible chromatin molecules.

| constraint | value |
| --- | --- |
| enum | `SNARE-Seq2-AC`, `bulkATACseq`, `snATACseq`, or `sciATACseq` |
| required | `True` |

<a name="transposition_transposase_source"></a>
##### [`transposition_transposase_source`](#transposition_transposase_source)
The source of the Tn5 transposase and transposon used for capturing accessible chromatin.

| constraint | value |
| --- | --- |
| enum | `10X snATAC`, `In-house`, or `Nextera` |
| required | `True` |

<a name="transposition_kit_number"></a>
##### [`transposition_kit_number`](#transposition_kit_number)
If Tn5 came from a kit, provide the catalog number. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |

<a name="library_construction_protocols_io_doi"></a>
##### [`library_construction_protocols_io_doi`](#library_construction_protocols_io_doi)
A link to the protocol document containing the library construction method (including version) that was used, e.g. "Smart-Seq2", "Drop-Seq", "10X v3". DOI for protocols.io referring to the protocol for this assay.

| constraint | value |
| --- | --- |
| required | `True` |
| pattern (regular expression) | <code>10\.17504/.*</code> |
| url | prefix: <code>https://dx.doi.org/</code> |

<a name="library_layout"></a>
##### [`library_layout`](#library_layout)
State whether the library was generated for single-end or paired end sequencing.

| constraint | value |
| --- | --- |
| enum | `single-end` or `paired-end` |
| required | `True` |

<a name="library_adapter_sequence"></a>
##### [`library_adapter_sequence`](#library_adapter_sequence)
Adapter sequence to be used for adapter trimming. Example: `CTGTCTCTTATACACATCT`.

| constraint | value |
| --- | --- |
| pattern (regular expression) | <code>[ATCG]+(\+[ATCG]+)?</code> |
| required | `True` |

<a name="cell_barcode_read"></a>
##### [`cell_barcode_read`](#cell_barcode_read)
Which read file contains the cell barcode.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="cell_barcode_offset"></a>
##### [`cell_barcode_offset`](#cell_barcode_offset)
Positions in the read at which the cell barcodes start. Cell barcodes are, for example, 3 x 8 bp sequences that are spaced by constant sequences (the offsets). First barcode at position 0, then 38, then 76. (Does not apply to SNARE-seq and BulkATAC.) Example: `0,0,38,76`.

| constraint | value |
| --- | --- |
| pattern (regular expression) | <code>\d+(,\d+)*</code> |
| required | `True` |

<a name="cell_barcode_size"></a>
##### [`cell_barcode_size`](#cell_barcode_size)
Length of the cell barcode in base pairs. Cell barcodes are, for example, 3 x 8 bp sequences that are spaced by constant sequences, the offsets. (Does not apply to SNARE-seq and BulkATAC.) Example: `16,8,8,8`.

| constraint | value |
| --- | --- |
| pattern (regular expression) | <code>\d+(,\d+)*</code> |
| required | `True` |

<a name="library_pcr_cycles"></a>
##### [`library_pcr_cycles`](#library_pcr_cycles)
Number of PCR cycles to enrich for accessible chromatin fragments.

| constraint | value |
| --- | --- |
| type | `integer` |
| required | `True` |

<a name="library_pcr_cycles_for_sample_index"></a>
##### [`library_pcr_cycles_for_sample_index`](#library_pcr_cycles_for_sample_index)
Number of PCR cycles performed for library generation (figure in Descriptions section)

| constraint | value |
| --- | --- |
| type | `integer` |
| required | `True` |

<a name="library_final_yield"></a>
##### [`library_final_yield`](#library_final_yield)
Total ng of library after final pcr amplification step.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

<a name="library_final_yield_unit"></a>
##### [`library_final_yield_unit`](#library_final_yield_unit)
Units for library_final_yield. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| enum | `ng` |
| required | `False` |
| required if | `library_final_yield` present |

<a name="library_average_fragment_size"></a>
##### [`library_average_fragment_size`](#library_average_fragment_size)
Average size in basepairs (bp) of sequencing library fragments estimated via gel electrophoresis or bioanalyzer/tapestation.

| constraint | value |
| --- | --- |
| type | `integer` |
| required | `True` |

<a name="sequencing_reagent_kit"></a>
##### [`sequencing_reagent_kit`](#sequencing_reagent_kit)
Reagent kit used for sequencing.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="sequencing_read_format"></a>
##### [`sequencing_read_format`](#sequencing_read_format)
Slash-delimited list of the number of sequencing cycles for, for example, Read1, i7 index, i5 index, and Read2. Example: `12/34/56`.

| constraint | value |
| --- | --- |
| pattern (regular expression) | <code>\d+(/\d+)+</code> |
| required | `True` |

<a name="sequencing_read_percent_q30"></a>
##### [`sequencing_read_percent_q30`](#sequencing_read_percent_q30)
Q30 is the weighted average of all the reads (e.g. # bases UMI * q30 UMI + # bases R2 * q30 R2 + ...)

| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |
| minimum | `0` |
| maximum | `100` |

<a name="sequencing_phix_percent"></a>
##### [`sequencing_phix_percent`](#sequencing_phix_percent)
Percent PhiX loaded to the run.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |
| minimum | `0` |
| maximum | `100` |

<a name="contributors_path"></a>
##### [`contributors_path`](#contributors_path)
Relative path to file with ORCID IDs for contributors for this dataset.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="data_path"></a>
##### [`data_path`](#data_path)
Relative path to file or directory with instrument data. Downstream processing will depend on filename extension conventions.

| constraint | value |
| --- | --- |
| required | `True` |

</details>


<br>

## Directory schemas
The HIVE will process each dataset with
[scATACseq Pipeline 1.4.3](https://github.com/hubmapconsortium/sc-atac-seq-pipeline/releases/tag/1.4.3).
<summary><b>Version 0.0 (use this one)</b></summary>

| pattern | required? | description |
| --- | --- | --- |
| <code>[^/]+\.fastq\.gz</code> | ✓ | Compressed FastQ file |
| <code>extras\/.*</code> |  | Folder for general lab-specific files related to the dataset. [Exists in all assays] |

