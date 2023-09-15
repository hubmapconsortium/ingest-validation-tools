```
codex TSV errors:
- 'On row 2, column "donor_id", value "BAD" fails because it does not match the expected
  pattern. Example: ABC123'
- 'On row 2, column "tissue_id", value "BAD" fails because it does not match the expected
  pattern. Example: ABC123-BL-1-2-3_456'
- On row 2, column "execution_datetime", value "BAD" fails because it is not in the
  format YYYY-MM-DD Hour:Minute.
Hint: 'If validation fails because of extra whitespace in the TSV, try:

  src/cleanup_whitespace.py --tsv_in original.tsv --tsv_out clean.tsv.'
```
REMINDER: Besides running validate_tsv.py, you should also run validate_upload.py before submission.
