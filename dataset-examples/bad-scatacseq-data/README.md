```
Metadata TSV Errors:
  dataset-examples/bad-scatacseq-data/submission/scatacseq-metadata.tsv (as scatacseq):
    Internal:
    - On row 2, column "sc_isolation_protocols_io_doi", value "" fails because constraint
      "required" is "True"
    - On row 2, column "library_construction_protocols_io_doi", value "" fails because
      constraint "required" is "True"
    External:
      row 2, referencing dataset-examples/bad-scatacseq-data/submission/dataset-1:
        Not allowed:
        - not-the-file-you-are-looking-for.txt
        - unexpected-directory/place-holder.txt
        Required but missing:
        - '[^/]+/[^/]+\.fastq\.gz'
```
