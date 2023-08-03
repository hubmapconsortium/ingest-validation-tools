---
title: Publication
schema_name: publication
category: Other TSVs
all_versions_deprecated: False
exclude_from_index: False
layout: default
---

Related files:

- [📝 Excel template](): For metadata entry.
- [📝 TSV template](): Alternative for metadata entry.



## Metadata schema

### Field types
- *Boolean* fields can be given as `TRUE`/`FALSE`, `True`/`False`, `true`/`false`, or `1`/`0`.  


<summary><b>Version 1 (current)</b> (draft) (TBD)</summary>


<details markdown="1" ><summary><b>Version 0</b></summary>


<a name="version"></a>
##### [`version`](#version)
Current version of metadata schema. Template provides the correct value.

| constraint | value |
| --- | --- |
| enum | `0` |
| required | `True` |

<a name="assay_type"></a>
##### [`assay_type`](#assay_type)
The specific type of assay being executed.

| constraint | value |
| --- | --- |
| enum | `publication` |
| required | `True` |

<a name="contributors_path"></a>
##### [`contributors_path`](#contributors_path)
Relative path to file with ORCID IDs for contributors for this dataset.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="data_path"></a>
##### [`data_path`](#data_path)
Relative path to file or directory with instrument data. Downstream processing will depend on filename extension conventions.

| constraint | value |
| --- | --- |
| required | `True` |

</details>


<br>

## Directory schemas
### Version 2

| pattern | required? | description |
| --- | --- | --- |
| <code>TODO</code> | ✓ | Directory structure not yet specified. |
| <code>extras/.*</code> |  | Free-form descriptive information supplied by the TMC |

### Version 0

| pattern | required? | description |
| --- | --- | --- |
| <code>(data)/.+</code> (example: <code>data/file1.ext</code>) | ✓ | Supplementary data files for the publication. All files referenced by the Vitessce visualization configurations in the vignettes must be included in this directory. |
| <code>(vignettes)/.+</code> | ✓ | Subdirectory containing Vitessce visualization files and a description of those files. |
| <code>(vignettes)/(vignette)_\d+/[^/]+\.json</code> (example: <code>vignettes/vignette_01/file1.json</code>) |  | Vitessce visualization configuration files. One or more visualization configurations can be provided per vignette. |
| <code>(vignettes)/(vignette)_\d+/(description)\.md</code> (example: <code>vignettes/vignette_02/description.md</code>) |  | Description of the vignette and titles for the visualization configuration files. |
| <code>extras/.*</code> |  | Free-form descriptive information supplied by the TMC |

