```
Metadata TSV Errors:
  dataset-examples/bad-codex-data/submission/codex-metadata.tsv (as codex):
    External:
      row 2, referencing dataset-examples/bad-codex-data/submission/dataset-1:
        Not allowed:
        - channelnames.txt
        - cyc002_reg001_200216_112537/bad
        - experiment.json
        - exposure_times.txt
        - segmentation.json
        Required but missing:
        - .+\.pdf
        - cyc.*_reg.*_.*/.*_.*_Z.*_CH.*\.tif
        - drv_[^/]+/channelNames\.txt
        - drv_[^/]+/experiment\.json
        - drv_[^/]+/exposure_times\.txt
        - drv_[^/]+/processed_[^/]+/.*
        - drv_[^/]+/segmentation\.json
        - src_[^/]+/channelnames\.txt
        - src_[^/]+/channelnames_report\.csv
      row 2, contributors dataset-examples/bad-codex-data/submission/contributors.tsv:
        Internal:
        - The value "bad-id" in row 2 and column 6 ("F") does not conform to the pattern
          constraint of "\d{4}-\d{4}-\d{4}-\d{3}[0-9X]"
      row 2, antibodies dataset-examples/bad-codex-data/submission/antibodies.tsv: "Invalid\
        \ ascii because ordinal not in range(128): \"mber\tconjugated_tag\n [ \xF0\
        \ ] \x9F\x98\x83\t\tbad-value\t\t\tinv\""
```
