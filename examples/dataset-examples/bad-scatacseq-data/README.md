```
Upload Errors:
  TSV Errors:
    examples/dataset-examples/bad-scatacseq-data/upload/scatacseq-metadata.tsv, column 'contributors_path', value '.':
    - 'Expected a TSV, but found a directory: examples/dataset-examples/bad-scatacseq-data/upload.'
  Directory Errors:
    examples/dataset-examples/bad-scatacseq-data/upload/scatacseq-metadata.tsv, column 'data_path', value 'dataset-1':
      examples/dataset-examples/bad-scatacseq-data/upload/dataset-1 (as scatacseq-v0):
        Not allowed:
        - not-the-file-you-are-looking-for.txt.
        - unexpected-directory/place-holder.txt.
        Required but missing:
        - '[^/]+\.fastq\.gz.'
Metadata TSV Validation Errors:
  Local Validation Errors:
    examples/dataset-examples/bad-scatacseq-data/upload/scatacseq-metadata.tsv (as scatacseq-v0):
    - On row 2, column "sc_isolation_protocols_io_doi", value "" fails because it
      must be filled out.
    - On row 2, column "library_construction_protocols_io_doi", value "" fails because
      it must be filled out.
Hint: 'If validation fails because of extra whitespace in the TSV, try:

  src/cleanup_whitespace.py --tsv_in original.tsv --tsv_out clean.tsv.'
```
