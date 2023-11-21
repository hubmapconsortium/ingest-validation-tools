```
Upload Errors:
  TSV Errors:
    examples/dataset-examples/bad-cedar-assay-histology/upload/contributors.tsv:
    - 'Missing fields: ["first_name", "is_contact", "last_name", "middle_name_or_initial",
      "name", "orcid_id"].'
  Directory Errors:
    examples/dataset-examples/bad-cedar-assay-histology/upload/bad-histology-metadata.tsv, row 2, column data_path:
      examples/dataset-examples/bad-cedar-assay-histology/upload/dataset-1 (as histology-v2):
        Not allowed:
        - microscope_hardware.json.
        - microscope_settings.json.
        Required but missing:
        - extras\/microscope_hardware\.json.
    examples/dataset-examples/bad-cedar-assay-histology/upload/bad-histology-metadata.tsv, row 3, column data_path:
      examples/dataset-examples/bad-cedar-assay-histology/upload/dataset-2 (as histology-v2):
        Not allowed:
        - microscope_hardware.json.
        - microscope_settings.json.
        Required but missing:
        - extras\/microscope_hardware\.json.
Hint: 'If validation fails because of extra whitespace in the TSV, try:

  src/cleanup_whitespace.py --tsv_in original.tsv --tsv_out clean.tsv.'
```
