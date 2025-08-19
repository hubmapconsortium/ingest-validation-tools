```
Spreadsheet Validator Errors:
  examples/dataset-examples/bad-cedar-assay-histology/upload/bad-histology-metadata.tsv:
  - On row 3, column "contributors_path", value "" fails because of error "missingRequired".
  examples/dataset-examples/bad-cedar-assay-histology/upload/contributors.tsv:
  - On row 2, column "orcid", value "0000-0002-8928-abcd" fails because of error "invalidValueFormat".
URL Check Errors:
  examples/dataset-examples/bad-cedar-assay-histology/upload/contributors.tsv:
  - 'On row 2, column "orcid", value "0000-0002-8928-abcd" fails because of error
    "Exception": ORCID 0000-0002-8928-abcd does not exist.'
Reference Errors:
  No References:
    Files:
    - unreferenced_file
Fatal Errors: Skipping plugin validation due to errors in upload metadata or dir structure.
```
