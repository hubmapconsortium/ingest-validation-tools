---
title: STARmap
schema_name: starmap
category: Spatial Transcriptomics
all_versions_deprecated: False
exclude_from_index: False
layout: default

---
Prepare your metadata based on the latest metadata schema using one of the template files below. See the instructions in the [Metadata Validation Workflow](https://docs.google.com/document/d/1lfgiDGbyO4K4Hz1FMsJjmJd9RdwjShtJqFYNwKpbcZY) document for more information on preparing and validating your metadata.tsv file prior to submission.

Related files:


- [📝 Excel template](https://raw.githubusercontent.com/hubmapconsortium/dataset-metadata-spreadsheet/main/starmap/latest/starmap.xlsx): For metadata entry.
- [📝 TSV template](https://raw.githubusercontent.com/hubmapconsortium/dataset-metadata-spreadsheet/main/starmap/latest/starmap.tsv): Alternative for metadata entry.




## Metadata schema


<summary><a href="https://openview.metadatacenter.org/templates/https:%2F%2Frepo.metadatacenter.org%2Ftemplates%2F1945fc9c-bc2d-43df-b954-efec087024cf"><b>Version 2 (use this one)</b></a></summary>



<br>

## Directory schemas
<summary><b>Version 2.0 (use this one)</b></summary>

| pattern | required? | description |
| --- | --- | --- |
| <code>extras\/.*</code> | ✓ | Folder for general lab-specific files related to the dataset. |
| <code>raw\/.*</code> | ✓ | This is a directory containing raw data. |
| <code>raw\/starmap\/.*</code> |  | All relevent raw files for STARmap. |
| <code>lab_processed\/.*</code> | ✓ | Experiment files that were processed by the lab generating the data. |
| <code>lab_processed\/starmap\/.*</code> |  | All relevent experiment files for STARmap. |

