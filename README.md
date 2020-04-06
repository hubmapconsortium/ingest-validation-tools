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
usage: validate.py [-h] --dir DIR --type
                   {atacseq-default,codex-akoya,codex-stanford} --donor_id ID
                   --tissue_id ID [--skip_data_path] [--logging LOG_LEVEL]

optional arguments:
  -h, --help            show this help message and exit
  --dir DIR             Directory to validate
  --type {atacseq-default,codex-akoya,codex-stanford}
                        Ingest data type
  --donor_id ID         HuBMAP Display ID of Donor
  --tissue_id ID        HuBMAP Display ID of Tissue
  --skip_data_path      If present, the data_path will not be validated
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
