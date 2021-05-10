```
Metadata TSV Errors:
  examples/dataset-examples/bad-missing-data/submission/codex-metadata.tsv (as codex):
    Internal:
    - On row 3, column "donor_id", value "missing-datapath" fails because constraint
      "pattern" is "[A-Z]+[0-9]+"
    - On row 3, column "data_path", value "" fails because constraint "required" is
      "True"
    External:
      row 2, referencing examples/dataset-examples/bad-missing-data/submission/dataset-1:
        No such file or directory: examples/dataset-examples/bad-missing-data/submission/dataset-1
      row 2, contributors examples/dataset-examples/bad-missing-data/submission/contributors-missing.tsv: File
        does not exist
      row 2, antibodies examples/dataset-examples/bad-missing-data/submission/antibodies-missing.tsv: File
        does not exist
      row 3, contributors examples/dataset-examples/bad-missing-data/submission/contributors-missing.tsv: File
        does not exist
      row 3, antibodies examples/dataset-examples/bad-missing-data/submission/antibodies-missing.tsv: File
        does not exist
Hint: 'If validation fails because of extra whitespace in the TSV, try:

  src/cleanup_whitespace.py --tsv_in original.tsv --tsv_out clean.tsv'
```
