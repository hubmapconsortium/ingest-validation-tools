```
usage: cleanup_whitespace.py [-h] (--tsv_path PATH | --encoding_test ENCODING)

Data providers may use the "--tsv_path" option to strip invisible characters
from TSVs. The cleaned TSV is printed to STDOUT: Use output redirection to
save.

optional arguments:
  -h, --help            show this help message and exit
  --tsv_path PATH       TSV to strip padding whitespace from
  --encoding_test ENCODING
                        Generate test TSV using this encoding
```
