```
Spreadsheet Validator Errors:
  examples/plugin-tests/expected-failure/upload/good-visium-rnaseq-metadata.tsv:
  - On row 1, column "parent_sample_id", value "" fails because of error "missingRequired".
  - On row 2, column "preparation_protocol_doi", value "wrong" fails because of error
    "invalidUrl".
Fatal Errors: 'Skipping plugins validation: errors in upload metadata or dir structure.'
```