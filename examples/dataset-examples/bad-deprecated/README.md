```
Metadata TSV Errors:
  examples/dataset-examples/bad-deprecated/upload/nano-metadata.tsv (as nano):
    External:
      row 2, data examples/dataset-examples/bad-deprecated/upload/abc:
        No such file or directory: examples/dataset-examples/bad-deprecated/upload/abc
      row 2, contributors examples/dataset-examples/bad-deprecated/upload/abc: File
        does not exist
Hint: 'If validation fails because of extra whitespace in the TSV, try:

  src/cleanup_whitespace.py --tsv_in original.tsv --tsv_out clean.tsv'
```
