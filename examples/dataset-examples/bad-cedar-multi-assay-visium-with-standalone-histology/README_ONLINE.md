```
Upload Errors:
  Directory Errors:
    ? examples/dataset-examples/bad-cedar-multi-assay-visium-with-standalone-histology-bad-dir-schema/upload/good-visium-histology-metadata.tsv,
      column 'data_path', value ./dataset-1
    : ? examples/dataset-examples/bad-cedar-multi-assay-visium-with-standalone-histology-bad-dir-schema/upload/dataset-1
        (as histology-v2)
      : Required but missing:
        - raw\/.*.
        - raw\/images\/.*.
        - raw\/images\/[^\/]+\.(?:xml|scn|vsi|ndpi|svs|czi|tiff).
Hint: 'If validation fails because of extra whitespace in the TSV, try:

  src/cleanup_whitespace.py --tsv_in original.tsv --tsv_out clean.tsv.'
```
