---
title: snm3C-seq
schema_name: snm3C-seq
category: Sequence Assays
all_versions_deprecated: False
exclude_from_index: False
layout: default

---
Prepare your metadata based on the latest metadata schema using one of the template files below. See the instructions in the [Metadata Validation Workflow](https://docs.google.com/document/d/1lfgiDGbyO4K4Hz1FMsJjmJd9RdwjShtJqFYNwKpbcZY) document for more information on preparing and validating your metadata.tsv file prior to submission.

This is the most recent metadata specification that needs to be followed for the submission of new data. See the [harmonized specification](https://docs.hubmapconsortium.org/assays/metadata/snm3C-seq.html) for a view of the metadata across this and any previous versions.

Related files:


- [📝 Excel template](https://raw.githubusercontent.com/hubmapconsortium/dataset-metadata-spreadsheet/main/snm3C-seq/latest/snm3C-seq.xlsx): For metadata entry.
- [📝 TSV template](https://raw.githubusercontent.com/hubmapconsortium/dataset-metadata-spreadsheet/main/snm3C-seq/latest/snm3C-seq.tsv): Alternative for metadata entry.


See the metadata and directory schemas for snm3C-seq below.

<a name="metadata-schema"></a>
## [Metadata schema](#metadata-schema)


<summary><a href="https://openview.metadatacenter.org/templates/https:%2F%2Frepo.metadatacenter.org%2Ftemplates%2Ff99a48eb-7d62-4f7e-92e5-1cee7d08e970"><b>Version 2 (use this one)</b></a></summary>



<br>

<a name="directory-schemas"></a>
## [Directory schemas](#directory-schemas)
<summary><b>Version 2.0 (use this one)</b></summary>

| pattern | required? | description |
| --- | --- | --- |
| <code>extras\/.*</code> | ✓ | Folder for general lab-specific files related to the dataset. |
| <code>raw\/.*</code> | ✓ | This is a directory containing raw data. |
| <code>raw\/snm3C_seq\/.*</code> |  | All relevant raw files for snm3C-seq. |
| <code>lab_processed\/.*</code> | ✓ | Experiment files that were processed by the lab generating the data. |
| <code>lab_processed\/snm3C_seq\/.*</code> |  | All relevant experiment files for snm3C-seq. |

