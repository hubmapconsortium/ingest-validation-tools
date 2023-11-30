---
title: RNAseq
schema_name: rnaseq
category: Sequence Assays
all_versions_deprecated: False
exclude_from_index: False
layout: default

---
Prepare your metadata based on the latest metadata schema using one of the template files below. See the instructions in the [Metadata Validation Workflow](https://docs.google.com/document/d/1lfgiDGbyO4K4Hz1FMsJjmJd9RdwjShtJqFYNwKpbcZY) document for more information on preparing and validating your metadata.tsv file prior to submission.

Related files:


- [📝 Excel template](https://raw.githubusercontent.com/hubmapconsortium/dataset-metadata-spreadsheet/main/rnaseq/latest/rnaseq.xlsx): For metadata entry.
- [📝 TSV template](https://raw.githubusercontent.com/hubmapconsortium/dataset-metadata-spreadsheet/main/rnaseq/latest/rnaseq.tsv): Alternative for metadata entry.




## Metadata schema


<summary><a href="https://openview.metadatacenter.org/templates/https:%2F%2Frepo.metadatacenter.org%2Ftemplates%2F944e5fa0-f68b-4bdd-8664-74a3909429a9"><b>Version 5 (use this one)</b></a></summary>


<summary><a href="https://openview.metadatacenter.org/templates/https:%2F%2Frepo.metadatacenter.org%2Ftemplates%2F24c264ea-1645-4b0c-8a3b-2cba184fde95"><b>Version 2</b></a></summary>


<br>

## Directory schemas
<summary><b>Version 2 (use this one)</b></summary>

| pattern | required? | description |
| --- | --- | --- |
| <code>extras\/.*</code> | ✓ | Folder for general lab-specific files related to the dataset. |
| <code>extras\/expected_cell_count\.txt</code> |  | The expected cell count for the RNA sequencing dataset. This is an optional file that, if present, will be used by the HIVE's RNA sequencing analysis pipeline. With some datasets, knowing the expected cell count has improved the output of the HIVE analysis pipeline. |
| <code>raw\/.*</code> | ✓ | All raw data files for the experiment. |
| <code>raw\/fastq\/.*</code> | ✓ | Raw sequencing files for the experiment. |
| <code>raw\/fastq\/RNA\/.*</code> | ✓ | Directory containing fastq files pertaining to RNAseq sequencing. |
| <code>raw\/fastq\/RNA\/[^\/]+_R[^\/]+\.fastq\.gz</code> | ✓ | This is a GZip'd version of the forward and reverse fastq files from RNAseq sequencing (R1 and R2). |
| <code>lab_processed\/.*</code> |  | Experiment files that were processed by the lab generating the data. |

