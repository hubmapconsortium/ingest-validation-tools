```
sample-section TSV errors:
- On row 2, column "sample_id", value "" fails because constraint "required" is "True"
- On row 2, column "source_storage_time_value", value "bad" fails because type is
  "number/default"
- On row 2, column "source_storage_time_unit", value "bad" fails because constraint
  "enum" is "['min', 'hours', 'days', 'years']"
- On row 2, column "preparation_media", value "bad" fails because constraint "enum"
  is "['PFA (4%)', 'Buffered Formalin (10% NBF)', 'Non-Buffered Formalin (FOR)', '1
  x PBS', 'OCT', 'CMC', 'MACS Tissue Storage Solution', 'RNAlater', 'Methanol', 'Non-aldehyde
  based without acetic acid (NAA)', 'Non-aldehyde with acetic acid (ACA)', 'PAXgene
  tissue (PXT)', 'Allprotect tissue reagent (ALL)', 'None']"
- On row 2, column "preparation_temperature", value "bad" fails because constraint
  "enum" is "['Liquid Nitrogen', 'Liquid Nitrogen Vapor', 'Dry Ice', '-80 Celsius',
  '-20 Celsius', '4 Celsius', '24 Celsius (Room Temperature)', '37 Celsius']"
- On row 2, column "processing_time_value", value "bad" fails because type is "number/default"
- On row 2, column "processing_time_unit", value "bad" fails because constraint "enum"
  is "['min', 'hours', 'days']"
- On row 2, column "storage_media", value "bad" fails because constraint "enum" is
  "['PFA (4%)', 'Buffered Formalin (10% NBF)', 'Non-Buffered Formalin (FOR)', '1 x
  PBS', 'OCT Embedded', 'CMC Embedded', 'OCT Embedded Cryoprotected (sucrose)', 'Paraffin
  Embedded', 'MACS Tissue Storage Solution', 'RNAlater', 'Methanol', 'Tris-EDTA',
  '70% ethanol', 'Serum + DMSO', 'DMSO (no serum)', 'PAXgene Tissue Kit (PXT)', 'Allprotect
  Tissue Reagent (ALL)', 'Sucrose Cryoprotection Solution', 'Carboxymethylcellulose
  (CMC)', 'None']"
- On row 2, column "storage_temperature", value "bad" fails because constraint "enum"
  is "['Liquid Nitrogen (Unspecified)', 'Liquid Nitrogen (Cryotube)', 'Liquid Nitrogen
  (Straw)', 'Liquid Nitrogen Vapor', 'Dry Ice', '-80 Celsius (Unspecified)', '-80
  Celsius (Cryotube)', '-80 Celsius (Straw)', '-20 Celsius', '4 Celsius', '24 Celsius
  (Room Temperature)', '37 Celsius']"
- On row 2, column "section_thickness_value", value "bad" fails because type is "number/default"
- On row 2, column "section_thickness_unit", value "bad" fails because constraint
  "enum" is "['um', 'mm', 'cm']"
- On row 2, column "section_index_number", value "bad" fails because type is "integer/default"
- On row 2, column "area_value", value "bad" fails because type is "number/default"
- On row 2, column "area_unit", value "bad" fails because constraint "enum" is "['mm^2',
  'um^2']"
Hint: 'If validation fails because of extra whitespace in the TSV, try:

  src/cleanup_whitespace.py --tsv_in original.tsv --tsv_out clean.tsv'
```
REMINDER: Besides running validate_tsv.py, you should also run validate_upload.py before submission.
