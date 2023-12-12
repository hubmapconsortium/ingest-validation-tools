---
title: RNAseq (with probes)
schema_name: rnaseq-with-probes
category: Sequence Assays
all_versions_deprecated: False
exclude_from_index: False
layout: default

---
Prepare your metadata based on the latest metadata schema using one of the template files below. See the instructions in the [Metadata Validation Workflow](https://docs.google.com/document/d/1lfgiDGbyO4K4Hz1FMsJjmJd9RdwjShtJqFYNwKpbcZY) document for more information on preparing and validating your metadata.tsv file prior to submission.

Related files:


- [📝 Excel template](https://raw.githubusercontent.com/hubmapconsortium/dataset-metadata-spreadsheet/main/rnaseq-with-probes/latest/rnaseq-with-probes.xlsx): For metadata entry.
- [📝 TSV template](https://raw.githubusercontent.com/hubmapconsortium/dataset-metadata-spreadsheet/main/rnaseq-with-probes/latest/rnaseq-with-probes.tsv): Alternative for metadata entry.




## Metadata schema


<summary><a href="https://openview.metadatacenter.org/templates/https:%2F%2Frepo.metadatacenter.org%2Ftemplates%2Fe4df583f-95df-4113-92dc-6e9b90124d9f"><b>Version 2 (use this one)</b></a></summary>



<br>

## Directory schemas
<summary><b>Version 2 (use this one)</b></summary>

| pattern | required? | description |
| --- | --- | --- |
| <code>extras\/.*</code> | ✓ | Folder for general lab-specific files related to the dataset. |
| <code>extras\/expected_cell_count\.txt</code> |  | The expected cell count for the RNA sequencing dataset. This is an optional file that, if present, will be used by the HIVE's RNA sequencing analysis pipeline. With some datasets, knowing the expected cell count has improved the output of the HIVE analysis pipeline. |
| <code>raw\/.*</code> | ✓ | All raw data files for the experiment. |
| <code>raw\/custom_probe_set\.csv</code> |  | This file should contain any custom probes used and must be included if the metadata field "is_custom_probes_used" is "Yes". The file should minimally include:target gene id, probe seq, probe id. The contents of this file are modeled after the 10x Genomics probe set file (see <https://support.10xgenomics.com/spatial-gene-expression-ffpe/probe-sets/probe-set-file-descriptions/probe-set-file-descriptions#probe_set_csv_file>). |
| <code>raw\/additional_panels_used\.csv</code> |  | If multiple commercial probe panels were used, then the primary probe panel should be selected in the "oligo_probe_panel" metadata field. The additional panels must be included in this file. Each panel record should include:manufacturer, model/name, product code. |
| <code>raw\/fastq\/.*</code> | ✓ | Raw sequencing files for the experiment. |
| <code>raw\/fastq\/oligo\/.*</code> | ✓ | Directory containing fastq files pertaining to oligo sequencing. |
| <code>raw\/fastq\/oligo\/[^\/]+_R[^\/]+\.fastq\.gz</code> | ✓ | This is a gzip version of the fastq file. This file contains the cell barcode and unique molecular identifier (technical). |
| <code>lab_processed\/.*</code> |  | Experiment files that were processed by the lab generating the data. |

