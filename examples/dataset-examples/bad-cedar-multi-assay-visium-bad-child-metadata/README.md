```
Spreadsheet Validator Errors:
  examples/dataset-examples/bad-cedar-multi-assay-visium-bad-child-metadata/upload/bad-visium-rnaseq-metadata.tsv:
  - On row 1, column "parent_sample_id", value "" fails because of error "missingRequired".
  - On row 2, column "preparation_protocol_doi", value "wrong" fails because of error
    "invalidUrl".
URL Check Errors:
  examples/dataset-examples/bad-cedar-multi-assay-visium-bad-child-metadata/upload/bad-visium-rnaseq-metadata.tsv:
  - 'On row 3, column "parent_sample_id", value "" fails because of error "HTTPError":
    404 Client Error: Not Found for url: https://entity.api.hubmapconsortium.org/entities/.'
Reference Errors:
  No References:
    Files:
    - unreferenced_file.
Fatal Errors: 'Skipping plugins validation: errors in upload metadata or dir structure.'
```