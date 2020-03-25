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
usage: validate.py [-h] [--logging LOG_LEVEL] DIRECTORY TYPE

positional arguments:
  DIRECTORY            Directory to validate
  TYPE                 Ingest data type

optional arguments:
  -h, --help           show this help message and exit
  --logging LOG_LEVEL
  ```
  
  ```
  $ src/generate.py -h
usage: generate.py [-h] {atacseq,codex} {template.tsv,schema.yaml,README.md}

positional arguments:
  {atacseq,codex}       What type to generate for
  {template.tsv,schema.yaml,README.md}
                        What kind of thing to generate

optional arguments:
  -h, --help            show this help message and exit
  ```

