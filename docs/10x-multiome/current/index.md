---
title: 10x Multiome
schema_name: 10x-multiome
category: Sequence Assays
all_versions_deprecated: False
exclude_from_index: False
layout: default

---
Prepare your metadata based on the latest metadata schema using one of the template files below. See the instructions in the [Metadata Validation Workflow](https://docs.google.com/document/d/1lfgiDGbyO4K4Hz1FMsJjmJd9RdwjShtJqFYNwKpbcZY) document for more information on preparing and validating your metadata.tsv file prior to submission.

Related files:


- [📝 Excel template](https://raw.githubusercontent.com/hubmapconsortium/dataset-metadata-spreadsheet/main/10x-multiome/latest/10x-multiome.xlsx): For metadata entry.
- [📝 TSV template](https://raw.githubusercontent.com/hubmapconsortium/dataset-metadata-spreadsheet/main/10x-multiome/latest/10x-multiome.tsv): Alternative for metadata entry.


REQUIRED - For this assay, you must also prepare and submit two additional metadata.tsv files following the metadata schemas linked here for [RNAseq](https://hubmapconsortium.github.io/ingest-validation-tools/rnaseq/current/) and [ATACseq](https://hubmapconsortium.github.io/ingest-validation-tools/atacseq/current/). For additional documentation on this dataset type, please visit [here](https://docs.google.com/document/d/1cVX_uMA5ehz3TBjrlXSb9KkRo8_5kcFUFhJaWeW9JyU).

## Metadata schema


<summary><a href="https://openview.metadatacenter.org/templates/https:%2F%2Frepo.metadatacenter.org%2Ftemplates%2F63c06fb2-4638-4979-aa97-5aff2a840156"><b>Version 2 (use this one)</b></a></summary>



<br>

## Directory schemas
<summary><b>Version 2.0 (use this one)</b></summary>

| pattern | required? | description |
| --- | --- | --- |
| <code>extras\/.*</code> | ✓ | Folder for general lab-specific files related to the dataset. |
| <code>extras\/expected_cell_count\.txt</code> |  | The expected cell count for the RNA sequencing dataset. This is an optional file that, if present, will be used by the HIVE's RNA sequencing analysis pipeline. With some datasets, knowing the expected cell count has improved the output of the HIVE analysis pipeline. |
| <code>raw\/.*</code> | ✓ | All raw data files for the experiment. |
| <code>raw\/fastq\/.*</code> | ✓ | Raw sequencing files for the experiment. |
| <code>raw\/fastq\/RNA\/.*</code> | ✓ | Directory containing fastq files pertaining to RNAseq sequencing. |
| <code>raw\/fastq\/RNA\/[^\/]+_R[^\/]+\.fastq\.gz</code> | ✓ | This is a GZip'd version of the forward and reverse fastq files from RNAseq sequencing (R1 and R2). |
| <code>raw\/fastq\/ATAC\/.*</code> | ✓ | Directory containing fastq files pertaining to ATACseq sequencing. |
| <code>raw\/fastq\/ATAC\/[^\/]+_R[^\/]+\.fastq\.gz</code> | ✓ | This is a GZip'd version of the fastq files containing the forward, reverse and barcode reads from ATACseq sequencing (R1, R2 and R3). Further, if the barcodes are in R3 (as with 10X) then the metadata field "barcode reads" would be set to "Read 2 (R2)" and the fastq file named "*_R2*fastq.gz" would be expected. |
| <code>lab_processed\/.*</code> |  | Experiment files that were processed by the lab generating the data. |

