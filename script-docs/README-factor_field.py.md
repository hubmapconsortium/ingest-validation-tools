```text
usage: factor_field.py [-h] --field NAME --input_dir IN --output_dir OUT

Factor out all variants of a given field. Typical use: src/factor_field.py \
--field resolution_z_value \ --input_dir src/ingest_validation_tools/table-
schemas/assays/ \ --output_dir src/ingest_validation_tools/table-
schemas/includes/fields

optional arguments:
  -h, --help        show this help message and exit
  --field NAME
  --input_dir IN    Directory to scan for instances of the field
  --output_dir OUT  Directory to write field extracts
```
