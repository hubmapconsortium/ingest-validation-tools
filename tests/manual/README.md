## Testing

Automated testing (e.g. via GitHub action or by running `./test.sh`) does not hit the [CEDAR Metadata Center Spreadsheet Validator](https://metadatacenter.github.io/spreadsheet-validator-docs/api-reference/) or [assayclassifier](https://github.com/hubmapconsortium/ingest-api/tree/main/src/routes/assayclassifier) endpoint, nor does it perform any URL checking. This directory contains methods for a) live testing against examples using `test-dataset-examples-online.sh` and b) updating fixture data and README.md files for offline automated testing using `update_test_data.py`.

# Testing online

Run the following from the top-level directory:

```
./tests/manual/test-dataset-examples-online.sh <globus_token> <optional:start_index>
```

This test mechanism calls validate_upload.py and does not update files. It is good for reliable manual online testing.

- $1 = globus_token: you can find your personal Globus token by logging in to a site that requires Globus authentication (e.g. https://ingest.hubmapconsortium.org/) and looking at the Authorization header for your request in the Network tab of your browser. Omit the "Bearer " prefix.
- $2 = start_index (optional): to avoid hitting APIs continuously when re-running tests, you can provide an index (starting at 0) to start at a specific test.

# update_test_data.py

Updates fixture data and README files in example directories. This mechanism does not call validate_upload.py, instead instantiating uploads for each example directory's upload data directly.

To update fixture data, run the following, specifying individual example directories or any/all of the following: "examples/dataset-examples", "examples/dataset-iec-examples", "examples/plugin-tests" (you can use just "examples/" if you want to update all three).

Here is an example command that would update all README.md and fixtures.json files in `examples/dataset-examples`:

```
env PYTHONPATH=/ingest-validation-tools python -m tests.manual.update_test_data -t "examples/dataset-examples" --globus_token <globus_token>
```

This tool can be run in a non-destructive way for testing by passing the `--dry_run` flag, possibly in combination with `--verbose` for more detailed output. Here is an example command that would show any diffs in all README.md and fixtures.json files in `examples/dataset-examples`, `dataset-iec-examples`, and `examples/plugin-tests` without writing any data:

```
env PYTHONPATH=/ingest-validation-tools python -m tests.manual.update_test_data -t "examples/dataset-examples/good-cedar-histology" --globus_token <globus_token> --verbose --dry_run
```

Run the following command for more comprehensive documentation:

```
env PYTHONPATH=/ingest-validation-tools python -m tests.manual.update_test_data --help
```

# Automated testing

Run `./test.sh` to perform all offline tests. This will mimic the behavior of the GitHub action that runs on push and creation of PRs.

To only run offline tests against dataset-examples and dataset-iec-examples (good for debugging):

```
env PYTHONPATH=/ingest-validation-tools python -m unittest tests.test_dataset_examples
```

## Manual Testing for Plugins

Plugins live in [https://github.com/hubmapconsortium/ingest-validation-tests](https://github.com/hubmapconsortium/ingest-validation-tests), requiring them to be tested manually rather than being added to automatic testing suite. To test plugins, first make sure you have [ingest-validation-tests properly installed](https://github.com/hubmapconsortium/ingest-validation-tools#running-plugin-tests).

Then, run the following from the top-level directory:

```
python -m unittest tests/manual/test_plugins.py
```
Note: you may need to prepend `env PYTHONPATH=/ingest-validation-tools` to this command. 

## Creating Tests

All new examples will need fixtures.json and README.md files. Run this to generate them:

```
env PYTHONPATH=/ingest-validation-tools python -m tests.manual.update_test_data -t <new_example_dir_path> --globus_token <globus_token>
```
