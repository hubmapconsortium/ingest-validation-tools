---
title: GeoMx (RNA) / GeoMx (protein) / GeoMx
schema_name: geomx
category: Spatial Transcriptomics
all_versions_deprecated: False
exclude_from_index: False
layout: default
---

Related files:

Excel and TSV templates for this schema will be available when the draft next-generation schema, to be used in all future submissions, is finalized (no later than Sept. 30).



## Metadata schema


<summary><a href="https://docs.google.com/spreadsheets/d/1kd1UQ2il-eW-MTM4iEotyAxa8M_hcwn8yQJTU_II-F8"><b>Version 2 (use this one)</b> (draft - submission of data prepared using this schema will be supported by Sept. 30)</a></summary>



<br>

## Directory schemas
<summary><a href="https://docs.google.com/spreadsheets/d/1LE-iyY2E6eP4E8jhgP6rhsvjESrdHXWYrMwKTvNkI5Y"><b>Version 2 (use this one)</b> (draft - submission of data prepared using this schema will be supported by Sept. 30) </a></summary>

<summary><b>Version 0</b></summary>

| pattern | required? | description |
| --- | --- | --- |
| <code>[^/]*[^/]*\.dcc</code> (example: <code>DSP-0000000000000-A-A01.dcc</code>) | ✓ | Digital counts file containing sample by probe counts. |
| <code>[^/]*\.pkc</code> | ✓ | JSON file which contains mapping from probe IDs to gene IDs. |
| <code>[^/]*\.xlsx</code> | ✓ | Excel formatted file containing experimental metadata output by experimental platform. |
| <code>extras\/.*</code> |  | Folder for general lab-specific files related to the dataset. [Exists in all assays] |

