```
Metadata TSV Errors:
  dataset-examples/bad-codex-data/submission/codex-metadata.tsv (as codex):
    External:
      row 2, referencing dataset-examples/bad-codex-data/submission/dataset-1:
        Not allowed:
        - cyc002_reg001_200216_112537/bad
        Required but missing:
        - channelnames_report\.csv
        - '[^/]+\.pdf'
        - cyc.*_reg.*_.*/.*_.*_Z.*_CH.*\.tif
      row 2, contributors dataset-examples/bad-codex-data/submission/contributors.tsv:
      - The value "bad-id" in row 2 and column 6 ("F") does not conform to the pattern
        constraint of "\d{4}-\d{4}-\d{4}-\d{4}"
```
