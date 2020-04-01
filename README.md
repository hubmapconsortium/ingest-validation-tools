# ingest-validation-tools
HuBMAP data submission guidelines,
and tools to confirm that submissions adhere to the guidelines

## Data Submitter Documentation

Documentation, metadata TSV templates, JSON schemas are [here](docs).

## Development

Checkout the project, cd, venv, and then:
```
pip install -r requirements.txt
pip install -r requirements-dev.txt
./test.sh
```

## Usage

The [examples here](tests/fixtures) show the kind of feedback the user gets when the structure is wrong.

Eventually, this should be available on PyPI, but for now, it is run from source.
Two scripts are available:
```
$ src/validate.py -h
usage: validate.py [-h] --dir DIR --type
                   {atacseq-default,codex-akoya,codex-stanford} --donor_id ID
                   --tissue_id ID [--logging LOG_LEVEL]

optional arguments:
  -h, --help            show this help message and exit
  --dir DIR             Directory to validate
  --type {atacseq-default,codex-akoya,codex-stanford}
                        Ingest data type
  --donor_id ID         HuBMAP Display ID of Donor
  --tissue_id ID        HuBMAP Display ID of Tissue
  --logging LOG_LEVEL
  ```

  ```
  $ src/generate.py -h
usage: generate.py [-h] {atacseq,codex} target

positional arguments:
  {atacseq,codex}  What type to generate
  target           Directory to write output to

optional arguments:
  -h, --help       show this help message and exit
  ```
