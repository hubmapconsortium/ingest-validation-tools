---
title: Stereo-seq
schema_name: stereo-seq
category: Spatial Transcriptomics
all_versions_deprecated: False
exclude_from_index: False
layout: default

---
Prepare your metadata based on the latest metadata schema using one of the template files below. See the instructions in the [Metadata Validation Workflow](https://docs.google.com/document/d/1lfgiDGbyO4K4Hz1FMsJjmJd9RdwjShtJqFYNwKpbcZY) document for more information on preparing and validating your metadata.tsv file prior to submission.

This is the most recent metadata specification that needs to be followed for the submission of new data. See the [harmonized specification](https://docs.hubmapconsortium.org/assays/metadata/stereo-seq.html) for a view of the metadata across this and any previous versions.

Related files:


- [📝 Excel template](https://raw.githubusercontent.com/hubmapconsortium/dataset-metadata-spreadsheet/main/stereo-seq/latest/stereo-seq.xlsx): For metadata entry.
- [📝 TSV template](https://raw.githubusercontent.com/hubmapconsortium/dataset-metadata-spreadsheet/main/stereo-seq/latest/stereo-seq.tsv): Alternative for metadata entry.




<a name="metadata-schema"></a>
## [Metadata schema](#metadata-schema)


<summary><a href="https://openview.metadatacenter.org/templates/https:%2F%2Frepo.metadatacenter.org%2Ftemplates%2Fe1c0c17b-374c-4b22-b211-fe2b0ededb68"><b>Version 3 (use this one)</b></a></summary>


<summary><a href="https://openview.metadatacenter.org/templates/https:%2F%2Frepo.metadatacenter.org%2Ftemplates%2Fead450b1-9229-4bf9-bbfc-8508f78069a8"><b>Version 2</b></a></summary>


<br>

<a name="directory-schemas"></a>
## [Directory schemas](#directory-schemas)
<summary><b>Version 2.0 (use this one)</b></summary>

| pattern | required? | description |
| --- | --- | --- |
| <code>extras\/.*</code> | ✓ | Folder for general lab-specific files related to the dataset. |
| <code>raw\/.*</code> | ✓ | This is a directory containing raw data. |
| <code>raw\/stereo_seq\/.*</code> |  | This is a directory containing raw data exclusive to Stereo-seq. |
| <code>lab_processed\/.*</code> | ✓ | Experiment files that were processed by the lab generating the data. |
| <code>lab_processed\/stereo_seq\/.*</code> |  | Experiment files that were processed by the lab generating the data exclusive to Stereo-seq. |

