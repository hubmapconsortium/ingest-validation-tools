```
Directory Errors:
  examples/dataset-examples/bad-cedar-dir-histology/upload/bad-histology-metadata.tsv:
  - 'Value "./dataset-1" in column "data_path" points to non-existent directory: "examples/dataset-examples/bad-cedar-dir-histology/upload/dataset-1".'
  examples/dataset-examples/bad-cedar-dir-histology/upload/wrong (as histology-v2.3):
  - Not allowed:
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
    - raw\/images\/[^\/]+\.(?:xml|scn|vsi|ndpi|svs|czi|tiff|qptiff).
Reference Errors:
  No References:
    Files:
    - unreferenced_file.
Fatal Errors: 'Skipping plugins validation: errors in upload metadata or dir structure.'
```
