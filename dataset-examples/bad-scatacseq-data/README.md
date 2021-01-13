```
Metadata TSV Errors:
  dataset-examples/bad-scatacseq-data/submission/scatacseq-metadata.tsv (as scatacseq):
    Internal:
    - Column 17 ("Q") is a required field, but row 2 has no value
    - Column 27 ("AA") is a required field, but row 2 has no value
    External:
      row 2, referencing dataset-examples/bad-scatacseq-data/submission/dataset-1:
        Not allowed:
        - not-the-file-you-are-looking-for.txt
        - unexpected-directory/place-holder.txt
        Required but missing:
        - .*\.fastq\.gz
      row 2, contributors dataset-examples/bad-scatacseq-data/submission/contributors.tsv:
        External:
          row 2, orcid_id 0000-0000-0000-000X: 404
      row 2, protocols_io_doi 10.17504/fake: 404
```
