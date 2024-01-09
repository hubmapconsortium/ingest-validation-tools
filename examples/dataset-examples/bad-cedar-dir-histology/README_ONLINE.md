```
Upload Errors:
  Directory Errors:
    ? examples/dataset-examples/bad-cedar-dir-histology/upload/bad-histology-metadata.tsv,
      column 'data_path', value './dataset-1'
    : examples/dataset-examples/bad-cedar-dir-histology/upload/dataset-1 (as histology-v2):
        No such file or directory: examples/dataset-examples/bad-cedar-dir-histology/upload/dataset-1
    examples/dataset-examples/bad-cedar-dir-histology/upload/bad-histology-metadata.tsv, column 'data_path', value './wrong':
      examples/dataset-examples/bad-cedar-dir-histology/upload/wrong (as histology-v2):
        Not allowed:
        - not-allowed.
        Required but missing:
        - extras\/.*.
        - extras\/microscope_hardware\.json.
        - lab_processed\/.*.
        - lab_processed\/images\/.*.
        - lab_processed\/images\/[^\/]*ome-tiff\.channels\.csv.
        - lab_processed\/images\/[^\/]+\.ome\.tiff.
        - raw\/.*.
        - raw\/images\/.*.
        - raw\/images\/[^\/]+\.(?:xml|scn|vsi|ndpi|svs|czi|tiff).
Reference Errors:
  No References:
    Files:
    - unreferenced_file.
Hint: 'If validation fails because of extra whitespace in the TSV, try:

  src/cleanup_whitespace.py --tsv_in original.tsv --tsv_out clean.tsv.'
```
