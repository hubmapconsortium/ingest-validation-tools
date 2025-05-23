---
title: Publication
schema_name: publication
category: Other TSVs
all_versions_deprecated: False
exclude_from_index: False
layout: default

---

Related files:

Excel and TSV templates for this schema will be available when the draft next-generation schema, to be used in all future submissions, is finalized (no later than Sept. 30).

The original publication specification can be found [here](https://hubmapconsortium.github.io/ingest-validation-tools/publication/)

## Metadata schema


<summary><b>Version 2 (use this one)</b> (draft - submission of data prepared using this schema will be supported by Sept. 30) (TBD)</summary>



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

