```
Upload Errors:
  TSV Errors:
    examples/dataset-examples/bad-scatacseq-data/upload (as scatacseq):
      row 2, contributors examples/dataset-examples/bad-scatacseq-data/upload: Expected
        a TSV, but found a directory.
  Directory Errors:
    examples/dataset-examples/bad-scatacseq-data/upload/dataset-1 (as scatacseq):
      row 2, data examples/dataset-examples/bad-scatacseq-data/upload/dataset-1:
        Not allowed:
        - not-the-file-you-are-looking-for.txt.
        - unexpected-directory/place-holder.txt.
        Required but missing:
        - '[^/]+\.fastq\.gz.'
Metadata TSV Validation Errors:
  Local Validation Errors:
    examples/dataset-examples/bad-scatacseq-data/upload/scatacseq-metadata.tsv (as scatacseq):
    - On row 2, column "sc_isolation_protocols_io_doi", value "" fails because it
      must be filled out.
    - On row 2, column "library_construction_protocols_io_doi", value "" fails because
      it must be filled out.
    - Row at position "3" is completely blank.
Hint: 'If validation fails because of extra whitespace in the TSV, try:

  src/cleanup_whitespace.py --tsv_in original.tsv --tsv_out clean.tsv.'
```
