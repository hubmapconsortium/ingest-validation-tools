---
title: ATACseq
schema_name: atacseq
category: Sequence Assays
all_versions_deprecated: False
exclude_from_index: False
layout: default

---
Prepare your metadata based on the latest metadata schema using one of the template files below. See the instructions in the [Metadata Validation Workflow](https://docs.google.com/document/d/1lfgiDGbyO4K4Hz1FMsJjmJd9RdwjShtJqFYNwKpbcZY) document for more information on preparing and validating your metadata.tsv file prior to submission.

Related files:


- [📝 Excel template](https://raw.githubusercontent.com/hubmapconsortium/dataset-metadata-spreadsheet/main/atacseq/latest/atacseq.xlsx): For metadata entry.
- [📝 TSV template](https://raw.githubusercontent.com/hubmapconsortium/dataset-metadata-spreadsheet/main/atacseq/latest/atacseq.tsv): Alternative for metadata entry.




## Metadata schema


<summary><a href="https://openview.metadatacenter.org/templates/https:%2F%2Frepo.metadatacenter.org%2Ftemplates%2F329f8a62-a468-4ba9-863d-fc0e328f896a"><b>Version 3 (use this one)</b></a></summary>


<summary><a href="https://openview.metadatacenter.org/templates/https:%2F%2Frepo.metadatacenter.org%2Ftemplates%2F329f8a62-a468-4ba9-863d-fc0e328f896a"><b>Version 2</b></a></summary>


<br>

## Directory schemas
<summary><b>Version 2 (use this one)</b></summary>

| pattern | required? | description |
| --- | --- | --- |
| <code>extras\/.*</code> | ✓ | Folder for general lab-specific files related to the dataset. |
| <code>raw\/.*</code> | ✓ | All raw data files for the experiment. |
| <code>raw\/fastq\/.*</code> | ✓ | Raw sequencing files for the experiment. |
| <code>raw\/fastq\/ATAC\/.*</code> | ✓ | Directory containing fastq files pertaining to ATACseq sequencing. |
| <code>raw\/fastq\/ATAC\/[^\/]+_R[^\/]+\.fastq\.gz</code> | ✓ | This is a GZip'd version of the fastq files containing the forward, reverse and barcode reads from ATACseq sequencing (R1, R2 and R3). Further, if the barcodes are in R3 (as with 10X) then the metadata field "barcode reads" would be set to "Read 2 (R2)" and the fastq file named "*_R2*fastq.gz" would be expected. |
| <code>lab_processed\/.*</code> |  | Experiment files that were processed by the lab generating the data. |

