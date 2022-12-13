```
Metadata TSV Errors:
  examples/dataset-examples/bad-mixed/upload/codex-metadata.tsv (as codex):
    Internal:
    - On row 2, column "donor_id", value "-INVALID-" fails because constraint "pattern"
      is "[A-Z]+[0-9]+"
    External:
      row 2, data examples/dataset-examples/bad-mixed/upload/bad-shared-dataset:
        Not allowed:
        - not-good-for-either-type.txt
        Required but missing:
        - (processed|drv_[^/]*)/.*
        - (raw|processed)/config\.txt|(src_[^/]*|drv_[^/]*)/[sS]egmentation\.json
        - (raw|src_.*)/.*
        - (raw|src_.*)/[cC]yc.*_reg.*/.*_Z.*_CH.*\.tif
        - (raw|src_[^/]*)/[Ee]xperiment\.json
      row 2, contributors examples/dataset-examples/bad-mixed/upload/contributors.tsv: File
        has no data rows.
      row 2, antibodies examples/dataset-examples/bad-mixed/upload/antibodies.tsv: File
        does not exist
  examples/dataset-examples/bad-mixed/upload/scatacseq-metadata.tsv (as scatacseq):
    Internal:
    - On row 2, column "donor_id", value "-INVALID-" fails because constraint "pattern"
      is "[A-Z]+[0-9]+"
    - On row 2, column "sc_isolation_protocols_io_doi", value "" fails because constraint
      "required" is "True"
    - On row 2, column "library_construction_protocols_io_doi", value "" fails because
      constraint "required" is "True"
    External:
      row 2, data examples/dataset-examples/bad-mixed/upload/bad-shared-dataset:
        Not allowed:
        - not-good-for-either-type.txt
        Required but missing:
        - '[^/]+\.fastq\.gz'
      row 2, contributors examples/dataset-examples/bad-mixed/upload/contributors.tsv: File
        has no data rows.
Reference Errors:
  Multiple References:
    bad-shared-dataset:
    - examples/dataset-examples/bad-mixed/upload/codex-metadata.tsv (row 2)
    - examples/dataset-examples/bad-mixed/upload/scatacseq-metadata.tsv (row 2)
Hint: 'If validation fails because of extra whitespace in the TSV, try:

  src/cleanup_whitespace.py --tsv_in original.tsv --tsv_out clean.tsv'
```
