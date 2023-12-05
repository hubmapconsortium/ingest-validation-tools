```
Upload Errors:
  Directory Errors:
    ? examples/dataset-examples/bad-cedar-multi-assay-visium-bad-dir-structure/upload/good-visium-assay-metadata.tsv,
      column 'data_path', value ./Visium_9OLC_A4_S1
    : examples/dataset-examples/bad-cedar-multi-assay-visium-bad-dir-structure/upload/Visium_9OLC_A4_S1 (as visium-no-probes-v2):
        Required but missing:
        - lab_processed\/.*.
        - lab_processed\/images\/.*.
        - lab_processed\/images\/[^\/]*ome-tiff\.channels\.csv.
        - lab_processed\/images\/[^\/]+\.ome\.tiff.
Hint: 'If validation fails because of extra whitespace in the TSV, try:

  src/cleanup_whitespace.py --tsv_in original.tsv --tsv_out clean.tsv.'
```
