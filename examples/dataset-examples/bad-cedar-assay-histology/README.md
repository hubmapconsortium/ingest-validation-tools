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
      - 'On row 2, column "parent_sample_id", value "wrong" fails because of error
        "HTTPError": 401 Client Error: Unauthorized for url: https://entity.api.hubmapconsortium.org/entities/wrong.'
      - 'On row 3, column "parent_sample_id", value "HBM854.FXDQ.783" fails because
        of error "HTTPError": 401 Client Error: Unauthorized for url: https://entity.api.hubmapconsortium.org/entities/HBM854.FXDQ.783'
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