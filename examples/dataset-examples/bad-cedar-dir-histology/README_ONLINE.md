```
Upload Errors:
  Directory Errors:
    examples/dataset-examples/bad-cedar-dir-histology/upload/bad-histology-metadata.tsv, row 2, column data_path:
      examples/dataset-examples/bad-cedar-dir-histology/upload/dataset-1 (as histology-v2):
        No such file or directory: examples/dataset-examples/bad-cedar-dir-histology/upload/dataset-1
    examples/dataset-examples/bad-cedar-dir-histology/upload/bad-histology-metadata.tsv, row 3, column data_path:
      examples/dataset-examples/bad-cedar-dir-histology/upload/wrong (as histology-v2):
        Not allowed:
        - not-allowed.
        Required but missing:
        - extras\/.*.
        - lab_processed\/.*.
        - lab_processed\/annotations\/[^\/]+-objects\.csv.
        - lab_processed\/annotations\/[^\/]+\.segmentations\.ome\.tiff.
        - lab_processed\/annotations\/segmentation-masks\.csv.
        - lab_processed\/images\/.*.
        - lab_processed\/images\/[^\/]+\.ome-tiff\.channels\.csv.
        - lab_processed\/images\/[^\/]+\.ome\.tiff.
        - microscope_hardware\.json.
        - raw\/.*.
        - raw\/images\/.*.
        - raw\/images\/[^\/]+\.(?:scn|vsi|ndpi|svs|czi|tiff).
        - raw\/images\/[^\/]+\.xml.
Reference Errors:
  No References:
    Files:
    - unreferenced_file.
Hint: 'If validation fails because of extra whitespace in the TSV, try:

  src/cleanup_whitespace.py --tsv_in original.tsv --tsv_out clean.tsv.'
```
