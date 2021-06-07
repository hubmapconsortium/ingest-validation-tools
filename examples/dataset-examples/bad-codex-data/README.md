```
Metadata TSV Errors:
  examples/dataset-examples/bad-codex-data/upload/codex-metadata.tsv (as codex):
    Internal:
    - On row 2, column "resolution_z_unit", value "None" fails because Required when
      resolution_z_value is filled
    External:
      row 2, data examples/dataset-examples/bad-codex-data/upload/dataset-1:
        Not allowed:
        - channelnames.txt
        - cyc002_reg001_200216_112537/bad
        - experiment.json
        - exposure_times.txt
        - segmentation.json
        Required but missing:
        - (processed|drv_)[^/]+/channelNames\.txt
        - (processed|drv_)[^/]+/processed_[^/]+/.*
        - (raw|src_)[^/]+/channelnames\.txt
        - (raw|src_)[^/]+/channelnames_report\.csv
        - (raw|src_)[^/]+/cyc.*_reg.*_.*/.*_.*_Z.*_CH.*\.tif
        - (raw|src_)[^/]+/experiment\.json
        - (raw|src_)[^/]+/exposure_times\.txt
        - (raw|src_)[^/]+/segmentation\.(json|txt)
        - .+\.pdf
      row 2, contributors examples/dataset-examples/bad-codex-data/upload/contributors.tsv:
      - On row 2, column "orcid_id", value "bad-id" fails because constraint "pattern"
        is "\d{4}-\d{4}-\d{4}-\d{3}[0-9X]"
      - 'On row 4, column "affiliation", value "somewhere3" fails because there is
        a run of 3 sequential items: Limit is 3. If correct, reorder rows.'
      row 2, antibodies examples/dataset-examples/bad-codex-data/upload/antibodies.tsv: "Invalid\
        \ ascii because ordinal not in range(128): \"mber\tconjugated_tag\n [ \xF0\
        \ ] \x9F\x98\x83\t\tbad-value\t\t\tinv\""
Hint: 'If validation fails because of extra whitespace in the TSV, try:

  src/cleanup_whitespace.py --tsv_in original.tsv --tsv_out clean.tsv'
```
