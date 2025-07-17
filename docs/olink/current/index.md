---
title: Olink
schema_name: olink
category: Proteomics
all_versions_deprecated: False
exclude_from_index: False
layout: default

---
Prepare your metadata based on the latest metadata schema using one of the template files below. See the instructions in the [Metadata Validation Workflow](https://docs.google.com/document/d/1lfgiDGbyO4K4Hz1FMsJjmJd9RdwjShtJqFYNwKpbcZY) document for more information on preparing and validating your metadata.tsv file prior to submission.

Related files:


- [📝 Excel template](https://raw.githubusercontent.com/hubmapconsortium/dataset-metadata-spreadsheet/main/olink/latest/olink.xlsx): For metadata entry.
- [📝 TSV template](https://raw.githubusercontent.com/hubmapconsortium/dataset-metadata-spreadsheet/main/olink/latest/olink.tsv): Alternative for metadata entry.


[This link](https://docs.google.com/spreadsheets/d/1YnmdTAA0Z9MKN3OjR3Sca8pz-LNQll91wdQoRPSP6Q4/edit#gid=0) lists the set of fields that are required in the OME TIFF file XML header.

## Metadata schema


<summary><a href="https://openview.metadatacenter.org/templates/https:%2F%2Frepo.metadatacenter.org%2Ftemplates%2Fc78c882d-ff27-473e-b318-540dc6e8034d"><b>Version 2 (use this one)</b></a></summary>



<br>

## Directory schemas
<summary><b>Version 2.0 (use this one)</b></summary>

| pattern | required? | description |
| --- | --- | --- |
| <code>extras\/.*</code> | ✓ | Folder for general lab-specific files related to the dataset. |
| <code>raw\/.*</code> | ✓ | This is a directory containing raw data. |
| <code>raw\/olink\/.*</code> |  | All relevent raw files for Olink. |
| <code>lab_processed\/.*</code> | ✓ | Experiment files that were processed by the lab generating the data. |
| <code>lab_processed\/olink\/.*</code> |  | All relevent experiment files for Olink. |

