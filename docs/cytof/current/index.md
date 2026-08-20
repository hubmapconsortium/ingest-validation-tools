---
title: CyTOF
schema_name: cytof
category: Flow Cytometry
all_versions_deprecated: False
exclude_from_index: False
layout: default

---
Prepare your metadata based on the latest metadata schema using one of the template files below. See the instructions in the [Metadata Validation Workflow](https://docs.google.com/document/d/1lfgiDGbyO4K4Hz1FMsJjmJd9RdwjShtJqFYNwKpbcZY) document for more information on preparing and validating your metadata.tsv file prior to submission.
This is the most recent metadata specification that needs to be followed for the submission of new data. See the [harmonized specification](https://docs.hubmapconsortium.org/assays/metadata/cytof.html) for a view of the metadata across this and any previous versions.

Related files:


- [📝 Excel template](https://raw.githubusercontent.com/hubmapconsortium/dataset-metadata-spreadsheet/main/cytof/latest/cytof.xlsx): For metadata entry.
- [📝 TSV template](https://raw.githubusercontent.com/hubmapconsortium/dataset-metadata-spreadsheet/main/cytof/latest/cytof.tsv): Alternative for metadata entry.




<a name="metadata-schema"></a>
## [Metadata schema](#metadata-schema)


<summary><a href="https://openview.metadatacenter.org/templates/https:%2F%2Frepo.metadatacenter.org%2Ftemplates%2F4cb5ad9a-e5cc-4c3f-98cd-e685330165a9"><b>Version 2 (use this one)</b></a></summary>



<br>

<a name="directory-schemas"></a>
## [Directory schemas](#directory-schemas)
<summary><b>Version 2.0 (use this one)</b></summary>

| pattern | required? | description |
| --- | --- | --- |
| <code>extras\/.*</code> | ✓ | Folder for general lab-specific files related to the dataset. |
| <code>raw\/.*</code> | ✓ | This is a directory containing raw data. |
| <code>raw\/[^\/]+\.(?:xlsx&#124;txt)$</code> |  | Instrument calibration file |
| <code>raw\/[^\/]+\.imd$</code> |  | The Integrated Mass Data (IMD) file contains raw, unprocessed data from a CyTOF mass cytometer, including the intensity measurements of each metal ion channel for every cell detected during a sample run, essentially providing the raw signal for each cell across all measured markers in a single file. This data is later converted into a more standard FCS file for analysis. |
| <code>raw\/[^\/]+\.fcs$</code> |  | Contains the raw data from a mass cytometry experiment in a matrix where each row represents a single cell and each column represents a different metal-labeled antibody channel, with the values in each cell signifying the ion count detected for that specific metal on that cell, allowing for the analysis of multiple cell surface markers on individual cells. |
| <code>lab_processed\/.*</code> | ✓ | Experiment files that were processed by the lab generating the data. |
| <code>lab_processed\/[^\/]+\.fcs$</code> | ✓ | **[QA/QC]** A lab normalized version of the raw FCS file described above. |

