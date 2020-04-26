<pre>
Metadata TSV Errors:
  examples/bad-mixed/submission/atacseq-metadata.tsv (as atacseq):
    Internal:
    - The value "-INVALID-" in row 2 and column 1 ("A") does not conform to the pattern
      constraint of "[A-Z]+[0-9]+"
    - Column 17 ("Q") is a required field, but row 2 has no value
    - Column 27 ("AA") is a required field, but row 2 has no value
    External:
      atacseq-metadata.tsv (row 2):
      - This string: not-good-for-either-type.txt
        doesn't match this pattern: \.fastq(\.gz)?$
  examples/bad-mixed/submission/codex-akoya-metadata.tsv (as codex-akoya):
    Internal:
    - The value "-INVALID-" in row 2 and column 1 ("A") does not conform to the pattern
      constraint of "[A-Z]+[0-9]+"
    External:
      codex-akoya-metadata.tsv (row 2):
      - This file: not-good-for-either-type.txt
        doesn't match exactly one of these:
        - $ref: '#/definitions/subdirectory'
        - properties:
            type:
              enum:
              - file
            name:
              enum:
              - experiment.json
              - exposure_times.txt
              - channelnames.txt
              - segmentation.json
      - This directory:
        - not-good-for-either-type.txt
        should contain:
          properties:
            name:
              enum:
              - segmentation.json
Reference Errors:
  Multiple References:
    bad-shared-dataset:
    - examples/bad-mixed/submission/atacseq-metadata.tsv (row 2)
    - examples/bad-mixed/submission/codex-akoya-metadata.tsv (row 2)
</pre>
