```
Upload Errors:
  Directory Errors:
    ? examples/dataset-examples/good-cedar-multi-assay-visium/upload/good-visium-assay-metadata.tsv,
      column 'data_path', value ./Visium_9OLC_A4_S1
    : Draft directory schema: visium-no-probes-v2
    ? examples/dataset-examples/good-cedar-multi-assay-visium/upload/good-visium-assay-metadata.tsv,
      column 'data_path', value ./Visium_9OLC_A4_S2
    : Draft directory schema: visium-no-probes-v2
    ? examples/dataset-examples/good-cedar-multi-assay-visium/upload/good-visium-assay-metadata.tsv,
      column 'data_path', value ./Visium_9OLC_I4_S1
    : Draft directory schema: visium-no-probes-v2
Hint: 'If validation fails because of extra whitespace in the TSV, try:

  src/cleanup_whitespace.py --tsv_in original.tsv --tsv_out clean.tsv.'
```