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
        - .+\.pdf
        - cyc.*_reg.*_.*/.*_.*_Z.*_CH.*\.tif
        - drv_[^/]+/channelNames\.txt
        - drv_[^/]+/experiment\.json
        - drv_[^/]+/exposure_times\.txt
        - drv_[^/]+/processed_[^/]+/.*
        - drv_[^/]+/segmentation\.json
        - src_[^/]+/channelnames\.txt
        - src_[^/]+/channelnames_report\.csv
      row 2, antibodies dataset-examples/bad-mixed/submission/antibodies.tsv:
        Internal:
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
      row 2, protocols_io_doi 10.17504/fake: 404
Reference Errors:
  Multiple References:
    bad-shared-dataset:
    - dataset-examples/bad-mixed/submission/codex-metadata.tsv (row 2)
    - dataset-examples/bad-mixed/submission/scatacseq-metadata.tsv (row 2)
```
