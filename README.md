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
$ src/validate.py -h
usage: validate.py [-h]
                   [--local_directory PATH | --globus_origin_directory ORIGIN_PATH]
                   [--type_metadata TYPE_PATH [TYPE_PATH ...]]
                   [--logging LOG_LEVEL]

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
$ src/generate.py -h
usage: generate.py [-h] {atacseq,codex} target

positional arguments:
  {atacseq,codex}  What type to generate
  target           Directory to write output to

optional arguments:
  -h, --help       show this help message and exit
```
