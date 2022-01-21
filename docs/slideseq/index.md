---
title: Slide-seq
schema_name: slideseq
category: Sequence assays
all_versions_deprecated: False
layout: default
---

Related files:

- [📝 Excel template](https://raw.githubusercontent.com/hubmapconsortium/ingest-validation-tools/main/docs/slideseq/slideseq-metadata.xlsx): For metadata entry.
- [📝 TSV template](https://raw.githubusercontent.com/hubmapconsortium/ingest-validation-tools/main/docs/slideseq/slideseq-metadata.tsv): Alternative for metadata entry.



## Directory schemas
### v0

| pattern | required? | description |
| --- | --- | --- |
| <code>[^/]+/alignment/Puck_[^/]+\.bam</code> | ✓ | aligned sequencing data from Slide-seq experiments against reference HG38 |
| <code>[^/]+/alignment/Puck_[^/]+_mapping_rate\.txt</code> | ✓ | mapping rate summary (~ 10 number of mapping statistics per puck) |
| <code>[^/]+/alignment/Puck_[^/]+_alignment_quality\.pdf</code> | ✓ | mapping quality plots (has unique and multiple alignment ratio, alignment scores alignment mismatch) |
| <code>[^/]+/alignment/Puck_[^/]+\.digital_expression\.txt\.gz</code> | ✓ | bead x gene expression matrix (csv file) |
| <code>[^/]+/alignment/Puck_[^/]+\.exonic\+intronic\.pdf</code> | ✓ | post alignment plots (qa/qc), plots of sequencing data, alignment and barcode matching |
| <code>[^/]+/barcode_matching/BeadBarcodes\.txt</code> | ✓ | barcodes of all sequenced beads (Many of these barcodes will not be in the matched_bead_barcodes files) |
| <code>[^/]+/barcode_matching/BeadLocations\.txt</code> | ✓ | spatial coordinates of all sequenced beads (1 to 1 correspondence with BeadBarcodes) |
| <code>[^/]+/barcode_matching/Puck_[^/]+_unique_matched_illumina_barcodes\.txt</code> | ✓ | matched Illumina barcodes (used by illumina sequencer) |
| <code>[^/]+/barcode_matching/Puck_[^/]+_matched_bead_barcodes\.txt</code> | ✓ | matched bead barcodes (these are the barcodes that matched bead on the puck) |
| <code>[^/]+/barcode_matching/Puck_[^/]+_matched_bead_locations\.txt</code> | ✓ | matched bead coordinates (these are the location of the barcodes that matched bead on the puck) |
| <code>[^/]+/fastq/Puck_[^/]+\.read1\.fastq\.gz</code> | ✓ | each puck will have 2 fastq files, this file contains the first set of paired reads |
| <code>[^/]+/fastq/Puck_[^/]+\.read2\.fastq\.gz</code> | ✓ | each puck will have 2 fastq files, this file contains the second set of paired reads |
| <code>extras/.*</code> |  | Free-form descriptive information supplied by the TMC |

## Metadata schema

### Field types
- *Boolean* fields can be given as `TRUE`/`FALSE`, `True`/`False`, `true`/`false`, or `1`/`0`.  


<details markdown="1" open="true"><summary><b>Version 1 (current)</b></summary>

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

</details>
<details markdown="1"><summary>Unique to this type</summary>

[`acquisition_instrument_vendor`](#acquisition_instrument_vendor)<br>
[`acquisition_instrument_model`](#acquisition_instrument_model)<br>
[`rnaseq_assay_method`](#rnaseq_assay_method)<br>
[`library_construction_protocols_io_doi`](#library_construction_protocols_io_doi)<br>
[`library_layout`](#library_layout)<br>
[`library_adapter_sequence`](#library_adapter_sequence)<br>
[`puck_id`](#puck_id)<br>
[`is_technical_replicate`](#is_technical_replicate)<br>
[`bead_barcode_read`](#bead_barcode_read)<br>
[`bead_barcode_offset`](#bead_barcode_offset)<br>
[`bead_barcode_size`](#bead_barcode_size)<br>
[`library_pcr_cycles`](#library_pcr_cycles)<br>
[`library_pcr_cycles_for_sample_index`](#library_pcr_cycles_for_sample_index)<br>
[`library_final_yield_value`](#library_final_yield_value)<br>
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
| enum | `Slide-seq` |
| required | `True` |

<a name="analyte_class"></a>
##### [`analyte_class`](#analyte_class)
Analytes are the target molecules being measured with the assay.

| constraint | value |
| --- | --- |
| enum | `RNA` |
| required | `True` |

<a name="is_targeted"></a>
##### [`is_targeted`](#is_targeted)
Specifies whether or not a specific molecule(s) is/are targeted for detection/measurement by the assay.

| constraint | value |
| --- | --- |
| type | `boolean` |
| required | `True` |

### Unique to this type

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

<a name="rnaseq_assay_method"></a>
##### [`rnaseq_assay_method`](#rnaseq_assay_method)
The kit used for the RNA sequencing assay.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="library_construction_protocols_io_doi"></a>
##### [`library_construction_protocols_io_doi`](#library_construction_protocols_io_doi)
A link to the protocol document containing the library construction method (including version) that was used, e.g. "Smart-Seq2", "Drop-Seq", "10X v3".

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
Adapter sequence to be used for adapter trimming.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="puck_id"></a>
##### [`puck_id`](#puck_id)
Slide-seq captures RNA sequence data on spatially barcoded arrays of beads. Beads are fixed to a slide in a region shaped like a round puck. Each puck has a unique puck_id.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="is_technical_replicate"></a>
##### [`is_technical_replicate`](#is_technical_replicate)
Is the sequencing reaction run in repliucate, TRUE or FALSE.

| constraint | value |
| --- | --- |
| type | `boolean` |
| required | `True` |

<a name="bead_barcode_read"></a>
##### [`bead_barcode_read`](#bead_barcode_read)
Which read file contains the bead barcode.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="bead_barcode_offset"></a>
##### [`bead_barcode_offset`](#bead_barcode_offset)
Position(s) in the read at which the bead barcode starts.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="bead_barcode_size"></a>
##### [`bead_barcode_size`](#bead_barcode_size)
Length of the bead barcode in base pairs.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="library_pcr_cycles"></a>
##### [`library_pcr_cycles`](#library_pcr_cycles)
Number of PCR cycles to amplify cDNA.

| constraint | value |
| --- | --- |
| type | `integer` |
| required | `True` |

<a name="library_pcr_cycles_for_sample_index"></a>
##### [`library_pcr_cycles_for_sample_index`](#library_pcr_cycles_for_sample_index)
Number of PCR cycles performed for library indexing.

| constraint | value |
| --- | --- |
| type | `integer` |
| required | `True` |

<a name="library_final_yield_value"></a>
##### [`library_final_yield_value`](#library_final_yield_value)
Total number of ng of library after final pcr amplification step. This is the concentration (ng/ul) * volume (ul)

| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

<a name="library_final_yield_unit"></a>
##### [`library_final_yield_unit`](#library_final_yield_unit)
Units of final library yield. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| enum | `ng` |
| required | `False` |
| units for | `library_final_yield_value` |

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
| enum | `Slide-seq` |
| required | `True` |

<a name="analyte_class"></a>
##### [`analyte_class`](#analyte_class)
Analytes are the target molecules being measured with the assay.

| constraint | value |
| --- | --- |
| enum | `RNA` |
| required | `True` |

<a name="is_targeted"></a>
##### [`is_targeted`](#is_targeted)
Specifies whether or not a specific molecule(s) is/are targeted for detection/measurement by the assay.

| constraint | value |
| --- | --- |
| type | `boolean` |
| required | `True` |

### Unique to this type

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

<a name="rnaseq_assay_method"></a>
##### [`rnaseq_assay_method`](#rnaseq_assay_method)
The kit used for the RNA sequencing assay.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="library_construction_protocols_io_doi"></a>
##### [`library_construction_protocols_io_doi`](#library_construction_protocols_io_doi)
A link to the protocol document containing the library construction method (including version) that was used, e.g. "Smart-Seq2", "Drop-Seq", "10X v3".

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
Adapter sequence to be used for adapter trimming.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="puck_id"></a>
##### [`puck_id`](#puck_id)
Slide-seq captures RNA sequence data on spatially barcoded arrays of beads. Beads are fixed to a slide in a region shaped like a round puck. Each puck has a unique puck_id.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="is_technical_replicate"></a>
##### [`is_technical_replicate`](#is_technical_replicate)
Is the sequencing reaction run in repliucate, TRUE or FALSE.

| constraint | value |
| --- | --- |
| type | `boolean` |
| required | `True` |

<a name="bead_barcode_read"></a>
##### [`bead_barcode_read`](#bead_barcode_read)
Which read file contains the bead barcode.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="bead_barcode_offset"></a>
##### [`bead_barcode_offset`](#bead_barcode_offset)
Position(s) in the read at which the bead barcode starts.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="bead_barcode_size"></a>
##### [`bead_barcode_size`](#bead_barcode_size)
Length of the bead barcode in base pairs.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="library_pcr_cycles"></a>
##### [`library_pcr_cycles`](#library_pcr_cycles)
Number of PCR cycles to amplify cDNA.

| constraint | value |
| --- | --- |
| type | `integer` |
| required | `True` |

<a name="library_pcr_cycles_for_sample_index"></a>
##### [`library_pcr_cycles_for_sample_index`](#library_pcr_cycles_for_sample_index)
Number of PCR cycles performed for library indexing.

| constraint | value |
| --- | --- |
| type | `integer` |
| required | `True` |

<a name="library_final_yield_value"></a>
##### [`library_final_yield_value`](#library_final_yield_value)
Total number of ng of library after final pcr amplification step. This is the concentration (ng/ul) * volume (ul)

| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

<a name="library_final_yield_unit"></a>
##### [`library_final_yield_unit`](#library_final_yield_unit)
Units of final library yield. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| enum | `ng` |
| required | `False` |
| units for | `library_final_yield_value` |

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
