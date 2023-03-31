```
codex TSV errors:
- On row 2, column "donor_id", value "BAD" fails because constraint "pattern" is "[A-Z]+[0-9]+"
- On row 2, column "tissue_id", value "BAD" fails because constraint "pattern" is
  "([A-Z]+[0-9]+)-[A-Z]{2}\d*(-\d+)+(_\d+)?"
- On row 2, column "execution_datetime", value "BAD" fails because type is "datetime/%Y-%m-%d
  %H:%M"
Hint: 'If validation fails because of extra whitespace in the TSV, try:

  src/cleanup_whitespace.py --tsv_in original.tsv --tsv_out clean.tsv'
```
REMINDER: Besides running validate_tsv.py, you should also run validate_upload.py before submission.
