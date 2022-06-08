```text
usage: validate_tsv.py [-h] --path PATH --schema
                       {sample,sample-block,sample-suspension,sample-section,antibodies,contributors,metadata}
                       [--output {as_md,as_text,as_text_list,as_yaml}]

Validate a HuBMAP TSV.

optional arguments:
  -h, --help            show this help message and exit
  --path PATH           TSV path
  --schema {sample,sample-block,sample-suspension,sample-section,antibodies,contributors,metadata}
  --output {as_md,as_text,as_text_list,as_yaml}

Exit status codes:
  0: Validation passed
  1: Unexpected bug
  2: User error
  3: Validation failed
```
