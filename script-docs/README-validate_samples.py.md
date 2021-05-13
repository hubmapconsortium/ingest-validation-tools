```text
usage: validate_samples.py [-h] --path PATH
                           [--output {as_browser,as_html_doc,as_html_fragment,as_md,as_text,as_text_list,as_yaml}]

Validate a HuBMAP Sample metadata TSV.

optional arguments:
  -h, --help            show this help message and exit
  --path PATH           Sample metadata.tsv path.
  --output {as_browser,as_html_doc,as_html_fragment,as_md,as_text,as_text_list,as_yaml}

Exit status codes: 0: Validation passed 1: Unexpected bug 2: User error 3:
Validation failed
```
