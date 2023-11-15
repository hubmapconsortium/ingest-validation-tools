```
Upload Errors:
  TSV Errors:
    examples/dataset-examples/bad-cedar-assay-histology/upload/bad-histology-metadata.tsv row 2, column 'contributors_path':
      Local Validation Errors:
        examples/dataset-examples/bad-cedar-assay-histology/upload/contributors.tsv (as contributors-v1):
        - 'Missing fields: ["is_contact"].'
Hint: 'If validation fails because of extra whitespace in the TSV, try:

  src/cleanup_whitespace.py --tsv_in original.tsv --tsv_out clean.tsv.'
```
