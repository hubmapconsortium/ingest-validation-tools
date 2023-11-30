```
sample-v0 TSV errors:
  Local Validation Errors:
    examples/tsv-examples/sample/bad-sample/upload/sample.tsv (as sample-v0):
    - On row 2, column "sample_id", value "" fails because it must be filled out.
    - On row 2, column "procedure_date", value "" fails because it must be filled
      out.
    - On row 2, column "pathologist_report", value "" fails because it must be filled
      out.
    - 'On row 2, column "specimen_preservation_temperature", value "-196 Celsius /
      -80 Celsius / -20 Celsius / Room Temperature" fails because it is not one of
      these: "Liquid Nitrogen", "Liquid Nitrogen Vapor", "Freezer (-80 Celsius)",
      "Freezer (-20 Celsius)", "Refrigerator (4 Celsius)", "Room Temperature".'
Hint: 'If validation fails because of extra whitespace in the TSV, try:

  src/cleanup_whitespace.py --tsv_in original.tsv --tsv_out clean.tsv.'
```
REMINDER: Besides running validate_tsv.py, you should also run validate_upload.py before submission.
