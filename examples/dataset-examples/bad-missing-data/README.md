```
Directory Errors:
  examples/dataset-examples/bad-missing-data/upload/codex-metadata.tsv:
  - 'On row(s) 2, column "data_path", value "dataset-1" points to non-existent directory:
    examples/dataset-examples/bad-missing-data/upload/dataset-1.'
Antibodies/Contributors Errors:
  examples/dataset-examples/bad-missing-data/upload/codex-metadata.tsv:
  - 'On row(s) 2, 3, column "antibodies_path", value "antibodies-missing.tsv" points
    to non-existent file: examples/dataset-examples/bad-missing-data/upload/antibodies-missing.tsv.'
  - 'On row(s) 2, 3, column "contributors_path", value "contributors-missing.tsv"
    points to non-existent file: examples/dataset-examples/bad-missing-data/upload/contributors-missing.tsv.'
Local Validation Errors:
  examples/dataset-examples/bad-missing-data/upload/codex-metadata.tsv (as codex-v0):
  - On row 2, column "operator", value "n/a" fails because "N/A" fields should just
    be left empty.
  - 'On row 3, column "donor_id", value "missing-datapath" fails because it does not
    match the expected pattern. Example: ABC123'
  - On row 3, column "data_path", value "" fails because it must be filled out.
Fatal Errors: 'Skipping plugins validation: errors in upload metadata or dir structure.'
```