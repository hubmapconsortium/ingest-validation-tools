```
Metadata TSV Errors:
  examples/dataset-examples/bad-scrnaseq-hca-v0/upload/metadata.tsv (as scrnaseq-hca):
    Internal:
    - On row 2, column "operator_email", value "123" fails because type is "string/email"
    - On row 2, column "pi_email", value "123" fails because type is "string/email"
    - On row 2, column "is_targeted", value "true" fails because constraint "enum"
      is "['TRUE', 'FALSE']"
    - On row 2, column "is_technical_replicate", value "false" fails because constraint
      "enum" is "['TRUE', 'FALSE']"
    External:
      row 2, data examples/dataset-examples/bad-scrnaseq-hca-v0/upload/data:
        No such file or directory: examples/dataset-examples/bad-scrnaseq-hca-v0/upload/data
Hint: 'If validation fails because of extra whitespace in the TSV, try:

  src/cleanup_whitespace.py --tsv_in original.tsv --tsv_out clean.tsv'
```
