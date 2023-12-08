```
Metadata TSV Validation Errors:
  CEDAR Validation Errors:
    examples/dataset-examples/bad-cedar-multi-assay-visium-bad-child-metadata/upload/bad-visium-rnaseq-metadata.tsv:
      URL Errors:
      - 'Row 3, field "parent_sample_id" with value "": 404 Client Error: Not Found
        for url: https://entity.api.hubmapconsortium.org/entities/.'
      Validation Errors:
      - On row 1, column "parent_sample_id", value "" fails because of error "missingRequired".
      - On row 2, column "preparation_protocol_doi", value "wrong" fails because of
        error "invalidUrl".
Reference Errors:
  No References:
    Files:
    - unreferenced_file.
Hint: 'If validation fails because of extra whitespace in the TSV, try:

  src/cleanup_whitespace.py --tsv_in original.tsv --tsv_out clean.tsv.'
```
