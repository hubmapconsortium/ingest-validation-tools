<pre>
Metadata TSV Errors:
  examples/bad-atacseq-data/submission/atacseq-metadata.tsv (as atacseq):
    Internal:
    - Column 17 ("Q") is a required field, but row 2 has no value
    - Column 27 ("AA") is a required field, but row 2 has no value
    External:
      atacseq-metadata.tsv (row 2):
      - This string: not-the-file-you-are-looking-for.txt
        doesn't match this pattern: \.fastq(\.gz)?$
      - This string: directory
        is not one of the expected enum values:
        - file
      - This string: unexpected-directory
        doesn't match this pattern: \.fastq(\.gz)?$
</pre>
