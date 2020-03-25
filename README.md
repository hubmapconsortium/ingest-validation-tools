# ingest-validation-tools
Testbed for ingest validation tools: Eventually, the code here will be used by the ingest pipeline,
but how that will be done is undetermined.

## Data Submitter Documentation

Documentation, metadata TSV templates, JSON schemas are [here](docs).

## Development

I'm not sure what kind of interface will be most useful,
so for now I'm ignoring questions of packaging.
There is an executable `validate.py`... but I don't know if that will stay.

For now, checkout the project, cd, venv, and then:
```
pip install -r requirements.txt
pip install -r requirements-dev.txt
./test.sh
```

## Examples

The [examples here](tests/fixtures) show the kind of feedback the user gets when the structure is wrong.
