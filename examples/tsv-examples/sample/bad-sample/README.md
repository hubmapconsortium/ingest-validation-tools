```
sample TSV errors:
- On row 2, column "sample_id", value "" fails because constraint "required" is "True"
- On row 2, column "procedure_date", value "" fails because constraint "required"
  is "True"
- On row 2, column "pathologist_report", value "" fails because constraint "required"
  is "True"
- On row 2, column "specimen_preservation_temperature", value "-196 Celsius / -80
  Celsius / -20 Celsius / Room Temperature" fails because constraint "enum" is "['Liquid
  Nitrogen', 'Liquid Nitrogen Vapor', 'Freezer (-80 Celsius)', 'Freezer (-20 Celsius)',
  'Refrigerator (4 Celsius)', 'Room Temperature']"
Hint: 'If validation fails because of extra whitespace in the TSV, try:

  src/cleanup_whitespace.py --tsv_in original.tsv --tsv_out clean.tsv'
```
REMINDER: Besides running validate_tsv.py, you should also run validate_upload.py before submission.
