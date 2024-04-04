```
Directory Errors:
  examples/dataset-examples/bad-scatacseq-data/upload/dataset-1 (as scatacseq-v0.0):
  - Not allowed:
    - not-the-file-you-are-looking-for.txt.
    - unexpected-directory/place-holder.txt.
    Required but missing:
    - '[^/]+\.fastq\.gz.'
Antibodies/Contributors TSV Errors:
  examples/dataset-examples/bad-scatacseq-data/upload/scatacseq-metadata.tsv: 'Error
    opening or reading value "." from column "contributors_path": Expected a TSV,
    but found a directory: examples/dataset-examples/bad-scatacseq-data/upload.'
Local Validation Errors:
  examples/dataset-examples/bad-scatacseq-data/upload/scatacseq-metadata.tsv (as scatacseq-v0):
  - On row 2, column "sc_isolation_protocols_io_doi", value "" fails because it must
    be filled out.
  - On row 2, column "library_construction_protocols_io_doi", value "" fails because
    it must be filled out.
  - On row 2, column "protocols_io_doi", value "10.17504/fake" fails because it is
    an invalid DOI.
```