```
Spreadsheet Validator Errors:
  examples/dataset-examples/bad-cedar-multi-assay-visium-bad-child-metadata/upload/bad-visium-rnaseq-metadata.tsv:
  - On row 4, column "preparation_protocol_doi", value "wrong" fails because of error
    "invalidUrl".
URL Check Errors:
  examples/dataset-examples/bad-cedar-multi-assay-visium-bad-child-metadata/upload/bad-visium-rnaseq-metadata.tsv:
  - 'On row 3, column "parent_sample_id", value "" fails because of error "AssertionError":
    Unable to check URL for column "parent_sample_id" on row 3: empty value.'
Reference Errors:
  No References:
    Files:
    - unreferenced_file
Fatal Errors: Skipping plugin validation due to errors in upload metadata or dir structure.
```
