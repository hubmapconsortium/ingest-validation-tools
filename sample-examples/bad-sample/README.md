```
Sample TSV Errors:
- On row 2, column "sample_id", value "" fails because constraint "required" is "True"
- On row 2, column "procedure_date", value "" fails because constraint "required"
  is "True"
- On row 2, column "pathologist_report", value "" fails because constraint "required"
  is "True"
- On row 2, column "specimen_preservation_temperature", value "-196 Celsius / -80
  Celsius / -20 Celsius / Room Temperature" fails because constraint "enum" is "['Liquid
  Nitrogen', 'Liquid Nitrogen Vapor', 'Freezer (-80 Celsius)', 'Freezer (-20 Celsius)',
  'Room Temperature']"
```
