Upload Errors: TSV Errors: examples/dataset-iec-examples/bad-example/upload/metadata.tsv row 2, column "contributors_path": Schema version is deprecated: contributors-v0
Upload Errors: Directory Errors: examples/dataset-iec-examples/bad-example/upload/metadata.tsv, row 2, column data_path: examples/dataset-iec-examples/bad-example/upload (as scatacseq-v0): Not allowed: should-not-be-here.txt.
Metadata TSV Validation Errors: Local Validation Errors: examples/dataset-iec-examples/bad-example/upload/metadata.tsv (as scatacseq-v0): On row 2, column "donor_id", value "bad-donor-id" fails because it does not match the expected pattern. Example: ABC123
Hint: If validation fails because of extra whitespace in the TSV, try:
src/cleanup_whitespace.py --tsv_in original.tsv --tsv_out clean.tsv.
