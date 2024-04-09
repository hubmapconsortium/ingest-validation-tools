```
Directory Errors:
  examples/dataset-examples/bad-missing-data/upload/codex-metadata.tsv:
  - 'Value "dataset-1" in column "data_path" points to non-existent directory: "examples/dataset-examples/bad-missing-data/upload/dataset-1".'
Antibodies/Contributors Errors:
  examples/dataset-examples/bad-missing-data/upload/codex-metadata.tsv:
  - 'Value "contributors-missing.tsv" in column "contributors_path" points to non-existent
    file: "examples/dataset-examples/bad-missing-data/upload/contributors-missing.tsv".'
  - 'Value "antibodies-missing.tsv" in column "antibodies_path" points to non-existent
    file: "examples/dataset-examples/bad-missing-data/upload/antibodies-missing.tsv".'
Local Validation Errors:
  examples/dataset-examples/bad-missing-data/upload/codex-metadata.tsv (as codex-v0):
  - On row 2, column "operator", value "n/a" fails because "N/A" fields should just
    be left empty.
  - 'On row 3, column "donor_id", value "missing-datapath" fails because it does not
    match the expected pattern. Example: ABC123'
  - On row 3, column "data_path", value "" fails because it must be filled out.
```