```
Preflight: 'Multi-assay TSV examples/dataset-examples/bad-cedar-multi-assay-visium-unreferenced-parent-path/upload/bad-visium-extra-paths-assay-metadata.tsv
  contains data paths that are not present in child assay TSVs. Data paths unique
  to parent: ["./Visium_9OLC_I4_S3"].'
Hint: 'If validation fails because of extra whitespace in the TSV, try:

  src/cleanup_whitespace.py --tsv_in original.tsv --tsv_out clean.tsv.'
```
