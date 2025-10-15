# Testing


## Running tests

### Metadata validation of a single TSV

To check just the metadata for a single TSV, use the [Metadata Spreadsheet Validator](https://metadatavalidator.metadatacenter.org/).

### Testing online

As a default behavior, testing (e.g. via GitHub action or by running `./test.sh`) does not hit the [CEDAR Metadata Center Spreadsheet Validator](https://metadatacenter.github.io/spreadsheet-validator-docs/api-reference/) or [assayclassifier](https://github.com/hubmapconsortium/ingest-api/tree/main/src/routes/assayclassifier) endpoint, nor does it perform any URL checking.

To test with API checks, run the following:

```
./test.sh -o <globus_token>
```

This will run tests with API calls but will not update any files. To automatically update example files, see [Updating examples](#updating-examples) below.

Additional flags are available to restrict to specific examples/Python tests, skip linting/formatting, and/or run the plugin tests that require the presence of `ingest-validation-tests`. Run this for help:

```
./test.sh --help
```

### Automated testing

Running `./test.sh` will mimic the behavior of the GitHub action that runs on push and creation of PRs.

### Plugin testing

Plugins live in [https://github.com/hubmapconsortium/ingest-validation-tests](https://github.com/hubmapconsortium/ingest-validation-tests), requiring them to be tested manually rather than being added to automatic testing suite. To test plugins, first make sure you have [ingest-validation-tests properly installed](https://github.com/hubmapconsortium/ingest-validation-tools#running-plugin-tests).

To just run Python unittests for plugins, run the following from the top-level directory:

```
python -m unittest tests/manual/test_plugins.py
```
Note: you may need to prepend `env PYTHONPATH=/ingest-validation-tools` to this command. 

You can run plugin tests online using the `test.sh` script:

```
./test.sh -o <globus_token> -d examples/plugin-tests
```
...or by adding the `-p` flag when running `test.sh`.

## Creating Tests

All new examples will need fixtures.json and README.md files. After adding the test data to its own directory under the appropriate `examples/` subdirectory, run this to generate required files:

```
env PYTHONPATH=/ingest-validation-tools python -m tests.manual.update_test_data -t <new_example_dir_path> --globus_token <globus_token>
```

## Updating examples

Tests that find differences between fixtures and test output will give instructions about how to see more information and/or update fixtures/README.

### Manually updating examples

Here is an example command that would update all README.md and fixtures.json files in `examples/dataset-examples`:

```
env PYTHONPATH=/ingest-validation-tools python -m tests.manual.update_test_data -t "examples/dataset-examples" --globus_token <globus_token>
```

You can specify individual example directories or any/all of the following: "examples/dataset-examples", "examples/dataset-iec-examples", "examples/plugin-tests" (you can use just "examples/" if you want to update all three).

This tool can be run in a non-destructive way for testing by passing the `--dry_run` flag, possibly in combination with `--verbose` for more detailed output. Here is an example command that would show any diffs in README.md and fixtures.json files in `examples/dataset-examples/good-cedar-histology` without writing any data:

```
env PYTHONPATH=/ingest-validation-tools python -m tests.manual.update_test_data -t "examples/dataset-examples/good-cedar-histology" --globus_token <globus_token> --verbose --dry_run
```

Run the following command for more comprehensive documentation:

```
env PYTHONPATH=/ingest-validation-tools python -m tests.manual.update_test_data --help
```
