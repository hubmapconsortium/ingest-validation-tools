---
title: Publication
schema_name: publication
category: Other TSVs
all_versions_deprecated: False
exclude_from_index: False
layout: default

---

Prepare your metadata based on the latest metadata schema using one of the template files below. See the instructions in the [Metadata Validation Workflow](https://docs.google.com/document/d/1lfgiDGbyO4K4Hz1FMsJjmJd9RdwjShtJqFYNwKpbcZY) document for more information on preparing and validating your metadata.tsv file prior to submission.

Related files:


- [📝 Excel template](https://raw.githubusercontent.com/hubmapconsortium/ingest-validation-tools/main/docs/publication/deprecated/publication-metadata.xlsx): For metadata entry.
- [📝 TSV template](https://raw.githubusercontent.com/hubmapconsortium/ingest-validation-tools/main/docs/publication/deprecated/publication-metadata.tsv): Alternative for metadata entry.

## Metadata schema


<summary><a href="https://hubmapconsortium.github.io/ingest-validation-tools/publication/"><b>Version 2 (use this one)</b></a></summary>

<br>

## Directory schemas
<summary><b>Version 2.2 (use this one)</b></summary>

| pattern | required? | description |
| --- | --- | --- |
| <code>extras\/.*</code> | ✓ | Folder for general lab-specific files related to the dataset. [Exists in all assays] |
| <code>data\/.*</code> (example: <code>data/file1.ext</code>) | ✓ | Folder for supplementary data files for the publication. All files referenced by the Vitessce visualization configurations in the vignettes must be included in this directory. |
| <code>vignettes\/.*</code> | ✓ | Subdirectory containing Vitessce visualization files and a description of those files. |
| <code>vignettes\/vignette_\d+\/[^\/]+\.json$</code> (example: <code>vignettes/vignette_01/file1.json</code>) |  | Vitessce visualization configuration files. One or more visualization configurations can be provided per vignette. |
| <code>vignettes\/vignette_\d+\/description\.md$</code> (example: <code>vignettes/vignette_02/description.md</code>) |  | Description of the vignette and titles for the visualization configuration files. |

<summary><b>Version 2.1</b></summary>

| pattern | required? | description |
| --- | --- | --- |
| <code>extras\/.*</code> | ✓ | Folder for general lab-specific files related to the dataset. [Exists in all assays] |
| <code>data\/.+</code> (example: <code>data/file1.ext</code>) | ✓ | Supplementary data files for the publication. All files referenced by the Vitessce visualization configurations in the vignettes must be included in this directory. |
| <code>vignettes\/.*</code> | ✓ | Subdirectory containing Vitessce visualization files and a description of those files. |
| <code>vignettes\/vignette_\d+\/[^\/]+\.json$</code> (example: <code>vignettes/vignette_01/file1.json</code>) |  | Vitessce visualization configuration files. One or more visualization configurations can be provided per vignette. |
| <code>vignettes\/vignette_\d+\/description\.md$</code> (example: <code>vignettes/vignette_02/description.md</code>) |  | Description of the vignette and titles for the visualization configuration files. |

<summary><b>Version 2.0</b></summary>

| pattern | required? | description |
| --- | --- | --- |
| <code>extras\/.*</code> | ✓ | Folder for general lab-specific files related to the dataset. [Exists in all assays] |
| <code>data\/.+</code> (example: <code>data/file1.ext</code>) | ✓ | Supplementary data files for the publication. All files referenced by the Vitessce visualization configurations in the vignettes must be included in this directory. |
| <code>vignettes\/.*</code> | ✓ | Subdirectory containing Vitessce visualization files and a description of those files. |
| <code>vignettes\/vignette_\d+\/[^\/]+\.json</code> (example: <code>vignettes/vignette_01/file1.json</code>) |  | Vitessce visualization configuration files. One or more visualization configurations can be provided per vignette. |
| <code>vignettes\/vignette_\d+\/description\.md</code> (example: <code>vignettes/vignette_02/description.md</code>) |  | Description of the vignette and titles for the visualization configuration files. |

