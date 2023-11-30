```
Upload Errors:
  TSV Errors:
    examples/dataset-examples/bad-missing-data/upload/codex-metadata.tsv, row 2, column 'contributors_path':
    - 'File does not exist: examples/dataset-examples/bad-missing-data/upload/contributors-missing.tsv.'
    examples/dataset-examples/bad-missing-data/upload/codex-metadata.tsv, row 3, column 'contributors_path':
    - 'File does not exist: examples/dataset-examples/bad-missing-data/upload/contributors-missing.tsv.'
    examples/dataset-examples/bad-missing-data/upload/codex-metadata.tsv, row 2, column 'antibodies_path':
    - 'File does not exist: examples/dataset-examples/bad-missing-data/upload/antibodies-missing.tsv.'
    examples/dataset-examples/bad-missing-data/upload/codex-metadata.tsv, row 3, column 'antibodies_path':
    - 'File does not exist: examples/dataset-examples/bad-missing-data/upload/antibodies-missing.tsv.'
  Directory Errors:
    examples/dataset-examples/bad-missing-data/upload/codex-metadata.tsv, row 2, column data_path:
      examples/dataset-examples/bad-missing-data/upload/dataset-1 (as codex-v1-with-dataset-json):
        No such file or directory: examples/dataset-examples/bad-missing-data/upload/dataset-1
Metadata TSV Validation Errors:
  Local Validation Errors:
    examples/dataset-examples/bad-missing-data/upload/codex-metadata.tsv (as codex-v0):
    - On row 2, column "operator", value "n/a" fails because "N/A" fields should just
      be left empty.
    - 'On row 3, column "donor_id", value "missing-datapath" fails because it does
      not match the expected pattern. Example: ABC123'
    - On row 3, column "data_path", value "" fails because it must be filled out.
Hint: 'If validation fails because of extra whitespace in the TSV, try:

  src/cleanup_whitespace.py --tsv_in original.tsv --tsv_out clean.tsv.'
```
