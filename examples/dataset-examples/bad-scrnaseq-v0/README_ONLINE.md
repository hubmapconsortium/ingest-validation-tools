```
Upload Errors:
  Directory Errors:
    examples/dataset-examples/bad-scrnaseq-v0/upload/metadata.tsv, row 2, column data_path:
      examples/dataset-examples/bad-scrnaseq-v0/upload/data (as scrnaseq-v0):
        No such file or directory: examples/dataset-examples/bad-scrnaseq-v0/upload/data.
Metadata TSV Validation Errors:
  Local Validation Errors:
    examples/dataset-examples/bad-scrnaseq-v0/upload/metadata.tsv (as scrnaseq-v0):
    - On row 2, column "protocols_io_doi", value "10.17504/123" fails because it is
      an invalid DOI.
    - On row 2, column "sc_isolation_protocols_io_doi", value "10.17504/123" fails
      because it is an invalid DOI.
    - On row 2, column "library_construction_protocols_io_doi", value "10.17504/123"
      fails because it is an invalid DOI.
Hint: 'If validation fails because of extra whitespace in the TSV, try:

  src/cleanup_whitespace.py --tsv_in original.tsv --tsv_out clean.tsv.'
```
