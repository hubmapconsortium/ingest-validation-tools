```
Metadata TSV Errors:
  dataset-examples/bad-mixed/submission/codex-metadata.tsv (as codex):
    Internal:
    - The value "-INVALID-" in row 2 and column 1 ("A") does not conform to the pattern
      constraint of "[A-Z]+[0-9]+"
    External:
      row 2, referencing dataset-examples/bad-mixed/submission/bad-shared-dataset:
        Not allowed:
        - not-good-for-either-type.txt
        Required but missing:
        - channelnames\.txt
        - channelnames_report\.csv
        - experiment\.json
        - exposure_times\.txt
        - '[^/]+\.pdf'
        - cyc.*_reg.*_.*/.*_.*_Z.*_CH.*\.tif
      row 2, antibodies dataset-examples/bad-mixed/submission/antibodies.tsv:
      - 'No such file or directory: ''dataset-examples/bad-mixed/submission/antibodies.tsv'''
  dataset-examples/bad-mixed/submission/scatacseq-metadata.tsv (as scatacseq):
    Internal:
    - The value "-INVALID-" in row 2 and column 1 ("A") does not conform to the pattern
      constraint of "[A-Z]+[0-9]+"
    - Column 17 ("Q") is a required field, but row 2 has no value
    - Column 27 ("AA") is a required field, but row 2 has no value
    External:
      row 2, referencing dataset-examples/bad-mixed/submission/bad-shared-dataset:
        Not allowed:
        - not-good-for-either-type.txt
        Required but missing:
        - .*\.fastq\.gz
Reference Errors:
  Multiple References:
    bad-shared-dataset:
    - dataset-examples/bad-mixed/submission/codex-metadata.tsv (row 2)
    - dataset-examples/bad-mixed/submission/scatacseq-metadata.tsv (row 2)
```
