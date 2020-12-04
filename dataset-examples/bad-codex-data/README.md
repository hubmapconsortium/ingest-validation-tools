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
      row 2, antibodies dataset-examples/bad-codex-data/submission/antibodies.tsv:
      - Column 1 ("A") is a required field, but row 2 has no value
      - Column 2 ("B") is a required field, but row 2 has no value
      - The value "bad-value" in row 2 and column 3 ("C") does not conform to the
        pattern constraint of "AB_\d+"
      - Column 4 ("D") is a required field, but row 2 has no value
      - Column 5 ("E") is a required field, but row 2 has no value
      - The value "invalid" in row 2 and column 6 ("F") does not conform to the pattern
        constraint of "1/\d+"
```
