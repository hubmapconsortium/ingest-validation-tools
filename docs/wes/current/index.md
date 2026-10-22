---
title: Whole Exome Sequencing (WES)
schema_name: wes
category: Sequence Assays
all_versions_deprecated: False
exclude_from_index: False
layout: default

---

Related files:

Excel and TSV templates for this schema will be available when the draft next-generation schema, to be used in all future submissions, is finalized (no later than Sept. 30).



<a name="metadata-schema"></a>
## [Metadata schema](#metadata-schema)


<summary><a href="https://openview.metadatacenter.org/templates/https:%2F%2Frepo.metadatacenter.org%2Ftemplates%2F9a0570b7-b0ee-4e7e-a413-f95ae2f6cde7"><b>Version 2 (use this one)</b> (draft - submission of data prepared using this schema will be supported by Sept. 30)</a></summary>



<br>

<a name="directory-schemas"></a>
## [Directory schemas](#directory-schemas)
<summary><b>Version 2.0 (use this one)</b></summary>

| pattern | required? | description |
| --- | --- | --- |
| <code>extras\/expected_cell_count\.txt$</code> |  | The expected cell count for the RNA sequencing dataset. This is an optional file that, if present, will be used by the HIVE's RNA sequencing analysis pipeline. With some datasets, knowing the expected cell count has improved the output of the HIVE analysis pipeline. |
| <code>raw\/.*</code> | ✓ | All raw data files for the experiment. |
| <code>raw\/fastq\/.*</code> | ✓ | Raw sequencing files for the experiment. |
| <code>raw\/fastq\/RNA\/.*</code> | ✓ | Directory containing fastq files pertaining to RNAseq sequencing. |
| <code>raw\/fastq\/RNA\/[^\/]+_R[^\/]+\.fastq\.gz$</code> | ✓ | This is a GZip'd version of the forward and reverse fastq files from RNAseq sequencing (R1 and R2). |
| <code>lab_processed\/.*</code> |  | Experiment files that were processed by the lab generating the data. |

