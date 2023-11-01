```
Upload Errors:
  TSV Errors:
    examples/dataset-examples/bad-cedar-assay-histology/upload/contributors.tsv:
    - 'Missing fields: ["first_name", "is_contact", "last_name", "middle_name_or_initial",
      "name", "orcid_id"].'
Hint: 'If validation fails because of extra whitespace in the TSV, try:

  src/cleanup_whitespace.py --tsv_in original.tsv --tsv_out clean.tsv.'
```
