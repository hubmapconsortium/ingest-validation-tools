```
Metadata TSV Errors:
  examples/dataset-examples/bad-scatacseq-data/submission/scatacseq-metadata.tsv (as scatacseq):
    Internal:
    - On row 2, column "sc_isolation_protocols_io_doi", value "" fails because constraint
      "required" is "True"
    - On row 2, column "library_construction_protocols_io_doi", value "" fails because
      constraint "required" is "True"
    - Row at position "3" is completely blank
    External:
      row 2, referencing examples/dataset-examples/bad-scatacseq-data/submission/dataset-1:
        Not allowed:
        - not-the-file-you-are-looking-for.txt
        - unexpected-directory/place-holder.txt
        Required but missing:
        - '[^/]+\.fastq\.gz'
      row 2, contributors examples/dataset-examples/bad-scatacseq-data/submission: Expected
        a TSV, but found a directory
      row 3, referencing examples/dataset-examples/bad-scatacseq-data/submission:
        Not allowed:
        - dataset-1/not-the-file-you-are-looking-for.txt
        - dataset-1/unexpected-directory/place-holder.txt
        - scatacseq-metadata.tsv
        Required but missing:
        - '[^/]+\.fastq\.gz'
Hint: 'If validation fails because of extra whitespace in the TSV, try:

  src/cleanup_whitespace.py --tsv_path original.tsv > clean.tsv'
```
