---
title: geomx
schema_name: geomx
category: Other TSVs
all_versions_deprecated: False
exclude_from_index: False
layout: default
---

Related files:

- [📝 Excel template](https://raw.githubusercontent.com/hubmapconsortium/ingest-validation-tools/main/docs/geomx/geomx-metadata.xlsx): For metadata entry.
- [📝 TSV template](https://raw.githubusercontent.com/hubmapconsortium/ingest-validation-tools/main/docs/geomx/geomx-metadata.tsv): Alternative for metadata entry.



## Directory schemas
### v2
<summary><a href="https://docs.google.com/spreadsheets/d/1LE-iyY2E6eP4E8jhgP6rhsvjESrdHXWYrMwKTvNkI5Y">Draft</a></summary>

### v0

| pattern | required? | description |
| --- | --- | --- |
| <code>[^/]*[^/]*\.dcc</code> (example: <code>DSP-0000000000000-A-A01.dcc</code>) | ✓ | Digital counts file containing sample by probe counts. |
| <code>[^/]*\.pkc</code> | ✓ | JSON file which contains mapping from probe IDs to gene IDs. |
| <code>[^/]*\.xlsx</code> | ✓ | Excel formatted file containing experimental metadata output by experimental platform. |
| <code>extras/.*</code> |  | Free-form descriptive information supplied by the TMC |





## Metadata schema

### Field types
- *Boolean* fields can be given as `TRUE`/`FALSE`, `True`/`False`, `true`/`false`, or `1`/`0`.  


<summary><a href="https://docs.google.com/spreadsheets/d/1kd1UQ2il-eW-MTM4iEotyAxa8M_hcwn8yQJTU_II-F8"><b>Version 2 (current)</b> (draft)</a></summary>

