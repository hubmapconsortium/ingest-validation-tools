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

<a name="metadata-schema"></a>
## [Metadata schema](#metadata-schema)


<details markdown="1" open="true"><summary><b>Version 2 (use this one)</b></summary>
We do not expect to receive any new data of this assay type.
If you are planning to submit new data of this assay type, reach out to help@hubmapconsortium.org.
</details>



<br>

<a name="directory-schemas"></a>
## [Directory schemas](#directory-schemas)
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

