```
antibodies-v30 TSV errors:
  examples/tsv-examples/contributors/bad-contributors/upload/contributors.tsv (as antibodies-v30): 'No
    such file or directory: src/ingest_validation_tools/others/antibodies-v30.yaml.'
Hint: 'If validation fails because of extra whitespace in the TSV, try:

  src/cleanup_whitespace.py --tsv_in original.tsv --tsv_out clean.tsv.'
```
REMINDER: Besides running validate_tsv.py, you should also run validate_upload.py before submission.
