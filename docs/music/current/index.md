---
title: MUSIC
schema_name: music
category: Sequence Assays
all_versions_deprecated: False
exclude_from_index: False
layout: default

---
Prepare your metadata based on the latest metadata schema using one of the template files below. See the instructions in the [Metadata Validation Workflow](https://docs.google.com/document/d/1lfgiDGbyO4K4Hz1FMsJjmJd9RdwjShtJqFYNwKpbcZY) document for more information on preparing and validating your metadata.tsv file prior to submission.

Related files:


- [📝 Excel template](https://raw.githubusercontent.com/hubmapconsortium/dataset-metadata-spreadsheet/main/music/latest/music.xlsx): For metadata entry.
- [📝 TSV template](https://raw.githubusercontent.com/hubmapconsortium/dataset-metadata-spreadsheet/main/music/latest/music.tsv): Alternative for metadata entry.




## Metadata schema


<summary><a href="https://openview.metadatacenter.org/templates/https:%2F%2Frepo.metadatacenter.org%2Ftemplates%2F5efe0d51-828c-457a-9b94-2ac8090fe14f"><b>Version 2 (use this one)</b></a></summary>



<br>

## Directory schemas
<summary><b>Version 2.0 (use this one)</b></summary>

| pattern | required? | description |
| --- | --- | --- |
| <code>extras\/.*</code> | ✓ | Folder for general lab-specific files related to the dataset. |
| <code>raw\/fastq\/[^\/]+_R[^\/]+\.fastq\.gz</code> | ✓ | The raw un-multiplexed fastq files. |
| <code>lab_processed\/fastq\/DNA\/[^\/]+_R[^\/]+\.fastq\.gz</code> | ✓ | This is a GZip'd version of the fastq files from whole genome sequencing. |
| <code>lab_processed\/fastq\/RNA\/[^\/]+_R[^\/]+\.fastq\.gz</code> | ✓ | This is a GZip'd version of the forward and reverse fastq files from RNAseq sequencing (R1 and R2). |

