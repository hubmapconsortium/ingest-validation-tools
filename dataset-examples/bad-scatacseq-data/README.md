```
Metadata TSV Errors:
  dataset-examples/bad-scatacseq-data/submission/scatacseq-metadata.tsv (as scatacseq):
    Internal:
    - On row 2, column "sc_isolation_protocols_io_doi", value "" fails because constraint
      "required" is "True"
    - On row 2, column "library_construction_protocols_io_doi", value "" fails because
      constraint "required" is "True"
    - Row at position "3" is completely blank
    External:
      row 2, referencing dataset-examples/bad-scatacseq-data/submission/dataset-1:
        Not allowed:
        - not-the-file-you-are-looking-for.txt
        - unexpected-directory/place-holder.txt
      row 2, contributors dataset-examples/bad-scatacseq-data/submission: Expected
        a TSV, but found a directory
      row 3, referencing dataset-examples/bad-scatacseq-data/submission:
        Not allowed:
        - dataset-1/not-the-file-you-are-looking-for.txt
        - dataset-1/unexpected-directory/place-holder.txt
        - scatacseq-metadata.tsv
      row 3, contributors dataset-examples/bad-scatacseq-data/submission: Expected
        a TSV, but found a directory
```
