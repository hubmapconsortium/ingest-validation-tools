---
title: LC-MS
schema_name: lcms
category: Mass Spectrometry
all_versions_deprecated: False
exclude_from_index: False
layout: default

---
Prepare your metadata based on the latest metadata schema using one of the template files below. See the instructions in the [Metadata Validation Workflow](https://docs.google.com/document/d/1lfgiDGbyO4K4Hz1FMsJjmJd9RdwjShtJqFYNwKpbcZY) document for more information on preparing and validating your metadata.tsv file prior to submission.

Related files:


- [📝 Excel template](https://raw.githubusercontent.com/hubmapconsortium/dataset-metadata-spreadsheet/main/lcms/latest/lcms.xlsx): For metadata entry.
- [📝 TSV template](https://raw.githubusercontent.com/hubmapconsortium/dataset-metadata-spreadsheet/main/lcms/latest/lcms.tsv): Alternative for metadata entry.




## Metadata schema


<summary><a href="https://openview.metadatacenter.org/templates/https:%2F%2Frepo.metadatacenter.org%2Ftemplates%2Fef090376-4e19-43cb-92c1-91a1d758ee6e"><b>Version 4 (use this one)</b></a></summary>



<br>

## Directory schemas
<summary><b>Version 2 (use this one)</b></summary>

| pattern | required? | description |
| --- | --- | --- |
| <code>extras\/.*</code> | ✓ | Folder for general lab-specific files related to the dataset. |
| <code>extras\/mass-spec_environment\.(?:json&#124;tsv)</code> |  | JSON or TSV file containing the machine parameters/settings. This is akin to the microscope_environment.json file that's used to describe the imaging equipment. |
| <code>raw\/.*</code> | ✓ | Raw data files for the experiment. |
| <code>raw\/[^\/]+\.raw</code> (example: <code>raw/20200707_rmi049_75umPLRPS_Kidney_GF10pc_VAN0003LK32_biorep05_techrep02.raw</code>) | ✓ | Raw mass spectrometry data from an assay of LC-MS, MS, LC-MS Bottom-Up, MS Bottom-Up, LC-MS Top-Down, or MS Top-Down that describes an analyte class of protein, metabolites, lipids, peptides, phosphopeptides, or glycans. |
| <code>raw\/[^\/]+\.(?:mzML&#124;d)</code> | ✓ | Raw mass spectrometry data from an assay of LC-MS, MS, LC-MS Bottom-Up, MS Bottom-Up, LC-MS Top-Down, or MS Top-Down that describes an analyte class of protein, metabolites, lipids, peptides, phosphopeptides, or glycans. |
| <code>lab_processed\/.*</code> | ✓ | Lab processed files |
| <code>lab_processed\/ID_search_results\/.*</code> | ✓ | Identification results. |
| <code>lab_processed\/ID_search_results\/[^\/]+\.csv</code> | ✓ | Annotated data describing (qualitative or quantitative) the proteins, metabolites, lipids, peptides, phosphopeptides, or glycans identified from the corresponding raw data. In the case of MS1 this file should include a list of features. |
| <code>lab_processed\/ID_metadata\/.*</code> | ✓ | Identification search parameters/metadata. |
| <code>lab_processed\/ID_metadata\/[^\/]+\.csv</code> | ✓ | Software settings used during the analyte identification process (e.g., from MaxQuant or Proteome Discoverer). |
| <code>lab_processed\/QC_results\/.*</code> |  | Output file resulting from QC analysis. |
| <code>lab_processed\/QC_results\/[^\/]+\.txt</code> |  | A list of metrics with the score of the current dataset that shows the quality of data collection. |
| <code>raw\/RNA\/.*</code> | ✓ | Directory containing fastq files pertaining to RNAseq sequencing. |
| <code>raw\/RNA\/[^\/]+_R\.fastq\.gz</code> | ✓ | This is a GZip'd version of the forward and reverse fastq files from RNAseq sequencing (R1 and R2). |

