```
Directory Errors:
  examples/dataset-iec-examples/bad-example/upload (as scatacseq-v0.0):
    Not allowed:
    - should-not-be-here.txt
Antibodies/Contributors Errors:
  examples/dataset-iec-examples/bad-example/upload/extras/contributors.tsv: No primary
    contact.
Local Validation Errors:
  examples/dataset-iec-examples/bad-example/upload/extras/contributors.tsv (as contributors-v0):
  - Schema version is deprecated.
  examples/dataset-iec-examples/bad-example/upload/metadata.tsv (as scatacseq-v0):
  - 'On row 2, column "donor_id", value "bad-donor-id" fails because it does not match
    the expected pattern. Example: ABC123.'
  - On row 2, column "protocols_io_doi", value "10.17504/fake" fails because it is
    an invalid DOI.
  - On row 2, column "sc_isolation_protocols_io_doi", value "10.17504/fake" fails
    because it is an invalid DOI.
  - On row 2, column "library_construction_protocols_io_doi", value "10.17504/fake"
    fails because it is an invalid DOI.
Fatal Errors: Skipping plugin validation due to errors in upload metadata or dir structure.
```