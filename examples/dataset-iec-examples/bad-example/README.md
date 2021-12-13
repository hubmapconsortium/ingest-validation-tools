In metadata.tsv (as scatacseq): Internal: On row 2, column "donor_id", value "bad-donor-id" fails because constraint "pattern" is "[A-Z]+[0-9]+".
In metadata.tsv (as scatacseq): Internal: On row 2, column "protocols_io_doi", value "10.17504/fake" fails because URL returned 404: "https://dx.doi.org/10.17504/fake".
In metadata.tsv (as scatacseq): Internal: On row 2, column "sc_isolation_protocols_io_doi", value "10.17504/fake" fails because URL returned 404: "https://dx.doi.org/10.17504/fake".
In metadata.tsv (as scatacseq): Internal: On row 2, column "library_construction_protocols_io_doi", value "10.17504/fake" fails because URL returned 404: "https://dx.doi.org/10.17504/fake".
In the dataset examples/dataset-iec-examples/bad-example/upload referenced on row 2, the file "should-not-be-here.txt" is not allowed.
In metadata.tsv (as scatacseq): External: row 2, contributors examples/dataset-iec-examples/bad-example/upload/extras/contributors.tsv: Schema version is deprecated: contributors-v0.
Hint: If validation fails because of extra whitespace in the TSV, try:
src/cleanup_whitespace.py --tsv_in original.tsv --tsv_out clean.tsv.
