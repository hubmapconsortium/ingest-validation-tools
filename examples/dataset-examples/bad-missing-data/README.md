```
Metadata TSV Errors:
  examples/dataset-examples/bad-missing-data/submission/codex-metadata.tsv (as codex):
    External:
      row 2, referencing examples/dataset-examples/bad-missing-data/submission/dataset-1:
        No such file or directory: examples/dataset-examples/bad-missing-data/submission/dataset-1
      row 2, contributors examples/dataset-examples/bad-missing-data/submission/contributors-missing.tsv: File
        does not exist
      row 2, antibodies examples/dataset-examples/bad-missing-data/submission/antibodies-missing.tsv: File
        does not exist
Hint: 'If validation fails because of extra whitespace in the TSV, try:

  src/cleanup_whitespace.py --tsv_in original.tsv --tsv_out clean.tsv'
```
