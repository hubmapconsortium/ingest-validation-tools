```
Metadata TSV Errors:
  examples/bad-mixed/submission/codex-akoya-metadata.tsv (as codex-akoya):
    Internal:
    - The value "-INVALID-" in row 2 and column 1 ("A") does not conform to the pattern
      constraint of "[A-Z]+[0-9]+"
    External:
      codex-akoya-metadata.tsv (row 2):
        Not allowed:
        - not-good-for-either-type.txt
        Required but missing:
        - channelnames.txt
        - experiment.json
        - exposure_times.txt
        - cyc*_reg*_*/*_*_Z*_CH*
  examples/bad-mixed/submission/scatacseq-metadata.tsv (as scatacseq):
    Internal:
    - The value "-INVALID-" in row 2 and column 1 ("A") does not conform to the pattern
      constraint of "[A-Z]+[0-9]+"
    - Column 17 ("Q") is a required field, but row 2 has no value
    - Column 27 ("AA") is a required field, but row 2 has no value
    External:
      scatacseq-metadata.tsv (row 2):
        Not allowed:
        - not-good-for-either-type.txt
        Required but missing:
        - '*.fastq.gz'
Reference Errors:
  Multiple References:
    bad-shared-dataset:
    - examples/bad-mixed/submission/codex-akoya-metadata.tsv (row 2)
    - examples/bad-mixed/submission/scatacseq-metadata.tsv (row 2)
```
