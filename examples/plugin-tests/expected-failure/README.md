/home/gesina/code/ingest-validation-tools/examples/plugin-tests/expected-failure/upload/Visium_9OLC_A4_S1/raw/images/faketiff.tiff is not a valid TIFF file: not a TIFF file
/home/gesina/code/ingest-validation-tools/examples/plugin-tests/expected-failure/upload/Visium_9OLC_A4_S1/lab_processed/images/Visium_90LC_A4_S1.ome.tiff is not a valid TIFF file: not a TIFF file
/home/gesina/code/ingest-validation-tools/examples/plugin-tests/expected-failure/upload/Visium_9OLC_I4_S1/raw/images/faketiff.tiff is not a valid TIFF file: not a TIFF file
/home/gesina/code/ingest-validation-tools/examples/plugin-tests/expected-failure/upload/Visium_9OLC_I4_S1/lab_processed/images/Visium_90LC_A4_S1.ome.tiff is not a valid TIFF file: not a TIFF file
/home/gesina/code/ingest-validation-tools/examples/plugin-tests/expected-failure/upload/Visium_9OLC_A4_S2/raw/images/faketiff.tiff is not a valid TIFF file: not a TIFF file
Threading at 4
Threading at 4
Added files from /home/gesina/code/ingest-validation-tools/examples/plugin-tests/expected-failure/upload/Visium_9OLC_A4_S1 to dirs_and_files: defaultdict(<class 'dict'>, {PosixPath('/home/gesina/code/ingest-validation-tools/examples/plugin-tests/expected-failure/upload/Visium_9OLC_A4_S1'): defaultdict(<class 'list'>, {PosixPath('raw/fastq/RNA'): [PosixPath('/home/gesina/code/ingest-validation-tools/examples/plugin-tests/expected-failure/upload/Visium_9OLC_A4_S1/raw/fastq/RNA/empty_R_file.fastq.gz')]})})
Added files from /home/gesina/code/ingest-validation-tools/examples/plugin-tests/expected-failure/upload/Visium_9OLC_A4_S2 to dirs_and_files: defaultdict(<class 'dict'>, {PosixPath('/home/gesina/code/ingest-validation-tools/examples/plugin-tests/expected-failure/upload/Visium_9OLC_A4_S1'): defaultdict(<class 'list'>, {PosixPath('raw/fastq/RNA'): [PosixPath('/home/gesina/code/ingest-validation-tools/examples/plugin-tests/expected-failure/upload/Visium_9OLC_A4_S1/raw/fastq/RNA/empty_R_file.fastq.gz')]}), PosixPath('/home/gesina/code/ingest-validation-tools/examples/plugin-tests/expected-failure/upload/Visium_9OLC_A4_S2'): defaultdict(<class 'list'>, {PosixPath('raw/fastq/RNA'): [PosixPath('/home/gesina/code/ingest-validation-tools/examples/plugin-tests/expected-failure/upload/Visium_9OLC_A4_S2/raw/fastq/RNA/empty_R_file.fastq.gz')]})})
Added files from /home/gesina/code/ingest-validation-tools/examples/plugin-tests/expected-failure/upload/Visium_9OLC_I4_S1 to dirs_and_files: defaultdict(<class 'dict'>, {PosixPath('/home/gesina/code/ingest-validation-tools/examples/plugin-tests/expected-failure/upload/Visium_9OLC_A4_S1'): defaultdict(<class 'list'>, {PosixPath('raw/fastq/RNA'): [PosixPath('/home/gesina/code/ingest-validation-tools/examples/plugin-tests/expected-failure/upload/Visium_9OLC_A4_S1/raw/fastq/RNA/empty_R_file.fastq.gz')]}), PosixPath('/home/gesina/code/ingest-validation-tools/examples/plugin-tests/expected-failure/upload/Visium_9OLC_A4_S2'): defaultdict(<class 'list'>, {PosixPath('raw/fastq/RNA'): [PosixPath('/home/gesina/code/ingest-validation-tools/examples/plugin-tests/expected-failure/upload/Visium_9OLC_A4_S2/raw/fastq/RNA/empty_R_file.fastq.gz')]}), PosixPath('/home/gesina/code/ingest-validation-tools/examples/plugin-tests/expected-failure/upload/Visium_9OLC_I4_S1'): defaultdict(<class 'list'>, {PosixPath('raw/fastq/RNA'): [PosixPath('/home/gesina/code/ingest-validation-tools/examples/plugin-tests/expected-failure/upload/Visium_9OLC_I4_S1/raw/fastq/RNA/empty_R_file.fastq.gz')]})})
Validating matching fastq file /home/gesina/code/ingest-validation-tools/examples/plugin-tests/expected-failure/upload/Visium_9OLC_I4_S1/raw/fastq/RNA/empty_R_file.fastq.gz
Validating empty_R_file.fastq.gz...
    → /home/gesina/code/ingest-validation-tools/examples/plugin-tests/expected-failure/upload/Visium_9OLC_I4_S1/raw/fastq/RNA/empty_R_file.fastq.gz
Validating matching fastq file /home/gesina/code/ingest-validation-tools/examples/plugin-tests/expected-failure/upload/Visium_9OLC_A4_S1/raw/fastq/RNA/empty_R_file.fastq.gz
Validating empty_R_file.fastq.gz...
    → /home/gesina/code/ingest-validation-tools/examples/plugin-tests/expected-failure/upload/Visium_9OLC_A4_S1/raw/fastq/RNA/empty_R_file.fastq.gz
Validating matching fastq file /home/gesina/code/ingest-validation-tools/examples/plugin-tests/expected-failure/upload/Visium_9OLC_A4_S2/raw/fastq/RNA/empty_R_file.fastq.gz
Validating empty_R_file.fastq.gz...
    → /home/gesina/code/ingest-validation-tools/examples/plugin-tests/expected-failure/upload/Visium_9OLC_A4_S2/raw/fastq/RNA/empty_R_file.fastq.gz
```
Plugin Errors:
  Recursively test all ome-tiff files for validity:
  - '/home/gesina/code/ingest-validation-tools/examples/plugin-tests/expected-failure/upload/Visium_9OLC_A4_S1/lab_processed/images/Visium_90LC_A4_S1.ome.tiff
    is not a valid OME.TIFF file: not a TIFF file.'
  - '/home/gesina/code/ingest-validation-tools/examples/plugin-tests/expected-failure/upload/Visium_9OLC_A4_S2/lab_processed/images/Visium_90LC_A4_S1.ome.tiff
    is not a valid OME.TIFF file: not a TIFF file.'
  - '/home/gesina/code/ingest-validation-tools/examples/plugin-tests/expected-failure/upload/Visium_9OLC_I4_S1/lab_processed/images/Visium_90LC_A4_S1.ome.tiff
    is not a valid OME.TIFF file: not a TIFF file.'
  Recursively test all tiff files that are not ome.tiffs for validity:
  - '/home/gesina/code/ingest-validation-tools/examples/plugin-tests/expected-failure/upload/Visium_9OLC_A4_S1/lab_processed/images/Visium_90LC_A4_S1.ome.tiff
    is not a valid TIFF file: not a TIFF file.'
  - '/home/gesina/code/ingest-validation-tools/examples/plugin-tests/expected-failure/upload/Visium_9OLC_A4_S1/raw/images/faketiff.tiff
    is not a valid TIFF file: not a TIFF file.'
  - '/home/gesina/code/ingest-validation-tools/examples/plugin-tests/expected-failure/upload/Visium_9OLC_A4_S2/lab_processed/images/Visium_90LC_A4_S1.ome.tiff
    is not a valid TIFF file: not a TIFF file.'
  - '/home/gesina/code/ingest-validation-tools/examples/plugin-tests/expected-failure/upload/Visium_9OLC_A4_S2/raw/images/faketiff.tiff
    is not a valid TIFF file: not a TIFF file.'
  - '/home/gesina/code/ingest-validation-tools/examples/plugin-tests/expected-failure/upload/Visium_9OLC_I4_S1/lab_processed/images/Visium_90LC_A4_S1.ome.tiff
    is not a valid TIFF file: not a TIFF file.'
  - '/home/gesina/code/ingest-validation-tools/examples/plugin-tests/expected-failure/upload/Visium_9OLC_I4_S1/raw/images/faketiff.tiff
    is not a valid TIFF file: not a TIFF file.'
Hint: 'If validation fails because of extra whitespace in the TSV, try:

  src/cleanup_whitespace.py --tsv_in original.tsv --tsv_out clean.tsv.'
```
