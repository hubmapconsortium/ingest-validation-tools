```text
usage: validate_tsv.py [-h] --path PATH --schema
                       {sample,sample-block,sample-suspension,sample-section,antibodies,contributors,metadata,source}
                       [--globus_token GLOBUS_TOKEN]
                       [--output {as_text,as_md}] [--app_context APP_CONTEXT]

Validate a HuBMAP TSV. REMINDER: Use of validate_tsv.py is deprecated; use the HuBMAP Metadata Spreadsheet Validator to validate single TSVs instead (https://metadatavalidator.metadatacenter.org).

optional arguments:
  -h, --help            show this help message and exit
  --path PATH           TSV path
  --schema {sample,sample-block,sample-suspension,sample-section,antibodies,contributors,metadata,source}
  --globus_token GLOBUS_TOKEN
                        Token for URL checking using Entity API.
  --output {as_text,as_md}
  --app_context APP_CONTEXT
                        App context values.

Exit status codes:
  0: Validation passed
  1: Unexpected bug
  2: User error
  3: Validation failed
```
