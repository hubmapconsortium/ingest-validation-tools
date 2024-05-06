```
Directory Errors:
  examples/dataset-examples/bad-codex-data/upload/dataset-1 (as codex-v1.1):
  - Not allowed:
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
Antibodies/Contributors Errors:
  examples/dataset-examples/bad-codex-data/upload/codex-metadata.tsv:
  - "Error opening or reading value \"antibodies.tsv\" from column \"antibodies_path\"\
    : Decode Error: Invalid ascii because ordinal not in range(128): \"mber\tconjugated_tag\n\
    \ [ \xF0 ] \x9F\x98\x83\t\tbad-value\t\t\tinv\"."
Local Validation Errors:
  examples/dataset-examples/bad-codex-data/upload/codex-metadata.tsv (as codex-v0):
  - On row 2, column "protocols_io_doi", value "10\.17504/protocols.io.menc3de" fails
    because it does not match the expected pattern.
  - On row 2, column "operator_email", value "no-at.example.com" fails because it
    is not a valid email.
  - On row 2, column "protocols_io_doi", value "10\.17504/protocols.io.menc3de" fails
    because it is an invalid DOI.
  - On row 2, column "resolution_z_unit", value "None" fails because it requires a
    value when resolution_z_value is filled.
  examples/dataset-examples/bad-codex-data/upload/contributors.tsv (as contributors-v1):
  - 'On row 2, column "orcid_id", value "bad-id" fails because it does not match the
    expected pattern. Example: 0000-0002-8928-741X.'
  - 'On row 2, column "orcid_id", value "bad-id" fails because URL returned 404: "https://pub.orcid.org/v3.0/bad-id".
    Example: 0000-0002-8928-741X.'
  - 'On row 3, column "orcid_id", value "0000-0000-0000-0000" fails because URL returned
    404: "https://pub.orcid.org/v3.0/0000-0000-0000-0000". Example: 0000-0002-8928-741X.'
  - 'On row 4, column "orcid_id", value "0000-0000-0000-0000" fails because URL returned
    404: "https://pub.orcid.org/v3.0/0000-0000-0000-0000". Example: 0000-0002-8928-741X.'
  - 'On row 4, column "affiliation", value "somewhere3" fails because there is a run
    of 3 sequential items: Limit is 3. If correct, reorder rows.'
Fatal Errors: 'Skipping plugins validation: errors in upload metadata or dir structure.'
```