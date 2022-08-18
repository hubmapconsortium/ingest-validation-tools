```
sample-block TSV errors:
- On row 2, column "sample_id", value "" fails because constraint "required" is "True"
Hint: 'If validation fails because of extra whitespace in the TSV, try:

  src/cleanup_whitespace.py --tsv_in original.tsv --tsv_out clean.tsv'
```
REMINDER: Besides running validate_tsv.py, you should also run validate_upload.py before submission.
