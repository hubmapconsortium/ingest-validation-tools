# ingest-validation-tools
HuBMAP data submission guidelines,
and tools which check that submissions adhere to those guidelines.

## HuBMAP submission structure:

Submissions are based on Globus directories containing:
- one or more `<type>-metadata.tsv` files.
- top-level subdirectories, or single files, in a 1-to-1 relationship with the rows of the TSVs.

## For data submitters:

Documentation, metadata TSV templates, JSON schemas are [here](docs).

## For curators:

You can run validation locally before the same checks are run automatically during ingest:
```
$ src/validate_submission.py -h
usage: validate_submission.py [-h]
                              [--local_directory PATH | --globus_origin_directory ORIGIN_PATH]
                              [--type_metadata TYPE_PATH [TYPE_PATH ...]]
                              [--logging LOG_LEVEL]

Validate HuBMAP submission, both the metadata TSVs, and the datasets

optional arguments:
  -h, --help            show this help message and exit
  --local_directory PATH
                        Local directory to validate
  --globus_origin_directory ORIGIN_PATH
                        A string of the form
                        "<globus_origin_id>:<globus_path>"
  --type_metadata TYPE_PATH [TYPE_PATH ...]
                        A string of the form "<atacseq-default|codex-
                        akoya|codex-stanford>:<local_path_to_tsv>"
  --logging LOG_LEVEL

Typical usecases:

  --type_metadata + --globus_origin_directory: Validate one or more
  local metadata.tsv files against a submission directory already on Globus.

  --globus_origin_directory: Validate a submission directory on Globus,
  with <type>-metadata.tsv files in place.

   --local_directory: Used in development against test fixtures, and in
   the ingest-pipeline, where Globus is the local filesystem.
  ```

## For developers:

Checkout the project, cd, venv, and then:
```
pip install -r requirements.txt
pip install -r requirements-dev.txt
./test.sh
```

After making tweaks to the schema, you can regenerate the docs:

```
$ src/generate_docs.py -h
usage: generate_docs.py [-h] {atacseq,codex} target

positional arguments:
  {atacseq,codex}  What type to generate
  target           Directory to write output to

optional arguments:
  -h, --help       show this help message and exit
```
