```
Upload Errors:
  TSV Errors:
    ? examples/dataset-examples/bad-cedar-assay-histology/upload/bad-histology-metadata.tsv,
      column 'contributors_path', value './contributors.tsv'
    : CEDAR Validation Errors:
        examples/dataset-examples/bad-cedar-assay-histology/upload/contributors.tsv:
          Validation Errors:
          - On row 0, column "orcid", value "0000-0002-8928-abcd" fails because of
            error "invalidValueFormat".
Metadata TSV Validation Errors:
  CEDAR Validation Errors:
    examples/dataset-examples/bad-cedar-assay-histology/upload/bad-histology-metadata.tsv:
      URL Errors:
      - 'Row 2, field "parent_sample_id" with value "wrong": Field value is not valid;
        URL https://entity.api.hubmapconsortium.org/entities/wrong returned a 400
        Error.'
      Validation Errors:
      - On row 0, column "parent_sample_id", value "wrong" fails because of error
        "invalidValueFormat".
      - On row 1, column "contributors_path", value "" fails because of error "missingRequired".
Reference Errors:
  No References:
    Files:
    - unreferenced_file.
Hint: 'If validation fails because of extra whitespace in the TSV, try:

  src/cleanup_whitespace.py --tsv_in original.tsv --tsv_out clean.tsv.'
```
