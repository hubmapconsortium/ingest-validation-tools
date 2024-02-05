```
Upload Errors:
  TSV Errors:
    examples/dataset-examples/bad-mixed/upload/codex-metadata.tsv, column 'contributors_path', value 'contributors.tsv':
    - 'File has no data rows: examples/dataset-examples/bad-mixed/upload/contributors.tsv.'
    examples/dataset-examples/bad-mixed/upload/codex-metadata.tsv, column 'antibodies_path', value 'antibodies.tsv':
    - 'File does not exist: examples/dataset-examples/bad-mixed/upload/antibodies.tsv.'
    examples/dataset-examples/bad-mixed/upload/scatacseq-metadata.tsv, column 'contributors_path', value 'contributors.tsv':
    - 'File has no data rows: examples/dataset-examples/bad-mixed/upload/contributors.tsv.'
  Directory Errors:
    examples/dataset-examples/bad-mixed/upload/codex-metadata.tsv, column 'data_path', value 'bad-shared-dataset':
      examples/dataset-examples/bad-mixed/upload/bad-shared-dataset (as codex-v1-with-dataset-json):
        Not allowed:
        - not-good-for-either-type.txt.
        Required but missing:
        - (processed|drv_[^/]*)/.*.
        - (raw|src_.*)/.*.
        - (raw|src_.*)/[cC]yc.*_reg.*/.*_Z.*_CH.*\.tif.
        - (raw|src_[^/]*)/dataset\.json.
        - extras/dir-schema-v1-with-dataset-json.
    examples/dataset-examples/bad-mixed/upload/scatacseq-metadata.tsv, column 'data_path', value 'bad-shared-dataset':
      examples/dataset-examples/bad-mixed/upload/bad-shared-dataset (as scatacseq-v0):
        Not allowed:
        - not-good-for-either-type.txt.
        Required but missing:
        - '[^/]+\.fastq\.gz.'
Metadata TSV Validation Errors:
  Local Validation Errors:
    examples/dataset-examples/bad-mixed/upload/codex-metadata.tsv (as codex-v0):
    - 'On row 2, column "donor_id", value "-INVALID-" fails because it does not match
      the expected pattern. Example: ABC123'
    examples/dataset-examples/bad-mixed/upload/scatacseq-metadata.tsv (as scatacseq-v0):
    - 'On row 2, column "donor_id", value "-INVALID-" fails because it does not match
      the expected pattern. Example: ABC123'
    - On row 2, column "sc_isolation_protocols_io_doi", value "" fails because it
      must be filled out.
    - On row 2, column "library_construction_protocols_io_doi", value "" fails because
      it must be filled out.
    - On row 2, column "protocols_io_doi", value "10.17504/fake" fails because it
      is an invalid DOI.
Reference Errors:
  Multiple References:
    bad-shared-dataset:
    - examples/dataset-examples/bad-mixed/upload/codex-metadata.tsv (row 2).
    - examples/dataset-examples/bad-mixed/upload/scatacseq-metadata.tsv (row 2).
Hint: 'If validation fails because of extra whitespace in the TSV, try:

  src/cleanup_whitespace.py --tsv_in original.tsv --tsv_out clean.tsv.'
```
