# ingest-validation-tools
Testbed for ingest validation tools: Eventually, the code here will be used by the ingest pipeline,
but how that will be done is undetermined.

## Roadmap

- Take the CSV structure described for [CODEX](https://docs.google.com/document/d/1CYYSXPQjwdbvmvZaEcsi_2udvDfGEZrMyh4yFnm4p3M/edit#)
and translate it into JSON Schema,
- such that [cidc-schemas](https://github.com/CIMAC-CIDC/cidc-schemas) can generate templates from it.
- *and*: We also want to validate directory structure: try our own [directory-schema](https://github.com/hubmapconsortium/directory-schema/).
- *and*: We also want integrity checks, like the linked sample ID matches sample ID in CSV, for example.

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

# Examples

The [examples here](src) show the kind of feedback the user gets when the structure is wrong.
