```
Upload Errors:
  TSV Errors:
    examples/dataset-examples/bad-codex-data/upload/codex-metadata.tsv, column 'contributors_path', value 'contributors.tsv':
      Local Validation Errors:
        examples/dataset-examples/bad-codex-data/upload/contributors.tsv (as contributors-v1):
        - 'On row 2, column "orcid_id", value "bad-id" fails because it does not match
          the expected pattern. Example: 0000-0002-8928-741X.'
        - 'On row 4, column "affiliation", value "somewhere3" fails because there
          is a run of 3 sequential items: Limit is 3. If correct, reorder rows.'
    examples/dataset-examples/bad-codex-data/upload/codex-metadata.tsv, column 'antibodies_path', value 'antibodies.tsv':
    - "Decode Error: Invalid ascii because ordinal not in range(128): \"mber\tconjugated_tag\n\
      \ [ \xF0 ] \x9F\x98\x83\t\tbad-value\t\t\tinv\"."
  Directory Errors:
    examples/dataset-examples/bad-codex-data/upload/codex-metadata.tsv, column 'data_path', value 'dataset-1':
      examples/dataset-examples/bad-codex-data/upload/dataset-1 (as codex-v1-with-dataset-json):
        Not allowed:
        - channelnames.txt.
        - cyc002_reg001_200216_112537/bad.
        - experiment.json.
        - exposure_times.txt.
        - segmentation.json.
        Required but missing:
        - (processed|drv_[^/]*)/.*.
        - (raw|src_.*)/.*.
        - (raw|src_.*)/[cC]yc.*_reg.*/.*_Z.*_CH.*\.tif.
        - (raw|src_[^/]*)/dataset\.json.
        - extras/dir-schema-v1-with-dataset-json.
Metadata TSV Validation Errors:
  Local Validation Errors:
    examples/dataset-examples/bad-codex-data/upload/codex-metadata.tsv (as codex-v0):
    - On row 2, column "protocols_io_doi", value "10\.17504/protocols.io.menc3de"
      fails because it does not match the expected pattern.
    - On row 2, column "operator_email", value "no-at.example.com" fails because it
      is not a valid email.
    - On row 2, column "resolution_z_unit", value "None" fails because it requires
      a value when resolution_z_value is filled.
Hint: 'If validation fails because of extra whitespace in the TSV, try:

  src/cleanup_whitespace.py --tsv_in original.tsv --tsv_out clean.tsv.'
```
