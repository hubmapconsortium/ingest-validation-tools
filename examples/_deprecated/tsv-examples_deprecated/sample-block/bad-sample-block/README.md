```
sample-block-v1 TSV errors:
  Local Validation Errors:
    examples/tsv-examples/sample-block/bad-sample-block/upload/sample-block.tsv (as sample-block-v1):
    - On row 2, column "sample_id", value "" fails because it must be filled out.
Hint: 'If validation fails because of extra whitespace in the TSV, try:

  src/cleanup_whitespace.py --tsv_in original.tsv --tsv_out clean.tsv.'
```
REMINDER: Besides running validate_tsv.py, you should also run validate_upload.py before submission.
