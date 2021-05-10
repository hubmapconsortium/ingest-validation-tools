```
Metadata TSV Errors:
  examples/dataset-examples/bad-codex-data/submission/codex-metadata.tsv (as codex):
    Internal:
    - On row 2, column "resolution_z_unit", value "None" fails because Required when
      resolution_z_value is filled
    External:
      row 2, referencing examples/dataset-examples/bad-codex-data/submission/dataset-1:
        Not allowed:
        - channelnames.txt
        - cyc002_reg001_200216_112537/bad
        - experiment.json
        - exposure_times.txt
        - segmentation.json
        Required but missing:
        - .+\.pdf
        - drv_[^/]+/channelNames\.txt
        - drv_[^/]+/processed_[^/]+/.*
        - src_[^/]+/channelnames\.txt
        - src_[^/]+/channelnames_report\.csv
        - src_[^/]+/cyc.*_reg.*_.*/.*_.*_Z.*_CH.*\.tif
        - src_[^/]+/experiment\.json
        - src_[^/]+/exposure_times\.txt
        - src_[^/]+/segmentation\.json
      row 2, contributors examples/dataset-examples/bad-codex-data/submission/contributors.tsv:
      - On row 2, column "orcid_id", value "bad-id" fails because constraint "pattern"
        is "\d{4}-\d{4}-\d{4}-\d{3}[0-9X]"
      - On row 4, column "affiliation", value "somewhere3" fails because incremented
        sequence of 3 items; limit is 3
      row 2, antibodies examples/dataset-examples/bad-codex-data/submission/antibodies.tsv: "Invalid\
        \ ascii because ordinal not in range(128): \"mber\tconjugated_tag\n [ \xF0\
        \ ] \x9F\x98\x83\t\tbad-value\t\t\tinv\""
Hint: 'If validation fails because of extra whitespace in the TSV, try:

  src/cleanup_whitespace.py --tsv_in original.tsv --tsv_out clean.tsv'
```
