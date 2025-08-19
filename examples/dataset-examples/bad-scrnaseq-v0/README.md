```
Directory Errors:
  examples/dataset-examples/bad-scrnaseq-v0/upload/metadata.tsv:
  - On row 2, column "data_path", value "data" points to non-existent directory "examples/dataset-examples/bad-scrnaseq-v0/upload/data".
Local Validation Errors:
  examples/dataset-examples/bad-scrnaseq-v0/upload/metadata.tsv (as scrnaseq-v0):
  - On row 2, column "protocols_io_doi", value "10.17504/123" fails because it is
    an invalid DOI.
  - On row 2, column "sc_isolation_protocols_io_doi", value "10.17504/123" fails because
    it is an invalid DOI.
  - On row 2, column "library_construction_protocols_io_doi", value "10.17504/123"
    fails because it is an invalid DOI.
Fatal Errors: Skipping plugin validation due to errors in upload metadata or dir structure.
```