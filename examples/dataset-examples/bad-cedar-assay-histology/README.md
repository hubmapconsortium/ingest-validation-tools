```
Spreadsheet Validator Errors:
  examples/dataset-examples/bad-cedar-assay-histology/upload/bad-histology-metadata.tsv:
  - On row 2, column "parent_sample_id", value "wrong" fails because of error "invalidValueFormat".
  - On row 3, column "contributors_path", value "" fails because of error "missingRequired".
  examples/dataset-examples/bad-cedar-assay-histology/upload/contributors.tsv:
  - On row 2, column "orcid", value "0000-0002-8928-abcd" fails because of error "invalidValueFormat".
URL Check Errors:
  examples/dataset-examples/bad-cedar-assay-histology/upload/bad-histology-metadata.tsv:
  - 'On row 2, column "parent_sample_id", value "wrong" fails because of error "HTTPError":
    Field value is not valid; URL https://entity.api.hubmapconsortium.org/entities/wrong
    returned a 400 Error.'
  examples/dataset-examples/bad-cedar-assay-histology/upload/contributors.tsv:
  - 'On row 2, column "orcid", value "0000-0002-8928-abcd" fails because of error
    "Exception": ORCID 0000-0002-8928-abcd does not exist.'
Reference Errors:
  No References:
    Files:
    - unreferenced_file.
Fatal Errors: 'Skipping plugins validation: errors in upload metadata or dir structure.'
```