---
title: G4X
schema_name: g4x
category: Spatial Transcriptomics
all_versions_deprecated: False
exclude_from_index: False
layout: default

---

Related files:

Excel and TSV templates for this schema will be available when the draft next-generation schema, to be used in all future submissions, is finalized (no later than Sept. 30).



## Metadata schema


<summary><a href="https://docs.google.com/spreadsheets/d/114DmeiACGQzA8C5ZY3mWh-338XNe7Zy7"><b>Version 2 (use this one)</b> (draft - submission of data prepared using this schema will be supported by Sept. 30)</a></summary>



<br>

## Directory schemas
<summary><b>Version 2.0 (use this one)</b></summary>

| pattern | required? | description |
| --- | --- | --- |
| <code>extras\/.*</code> | ✓ | Folder for general lab-specific files related to the dataset. |
| <code>raw\/.*</code> | ✓ | This is a directory containing raw data. |
| <code>raw\/g4x\/.*</code> |  | This is a directory containing raw data exclusive to G4X. |
| <code>lab_processed\/.*</code> | ✓ | Experiment files that were processed by the lab generating the data. |
| <code>lab_processed\/g4x\/.*</code> |  | Experiment files that were processed by the lab generating the data exclusive to G4X. |

