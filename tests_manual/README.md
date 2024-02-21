## Testing for Next-Gen Templates

Automated testing does not hit the CEDAR API or assayclassifier endpoint, nor does it perform any URL checking. This directory contains methods for a) live testing against examples using `test-dataset-examples-cedar.sh` and b) updating fixture data and README.md files for offline automated testing using `update_test_data.py`.

To manually test CEDAR validation including API calls, run the following from the top-level directory:

# ./tests-manual/test-dataset-examples-cedar.sh <globus_token> <start_index>

This test mechanism calls validate_upload.py and does not update files.

- $1 = globus_token: you can find your personal Globus token by logging in to a site that requires Globus authentication (e.g. https://ingest.hubmapconsortium.org/) and looking at the Authorization header for your request in the Network tab of your browser. Omit the "Bearer " prefix.
- $2 = start_index (optional): to avoid hitting APIs continuously when re-running tests, you can provide an index (starting at 0) to start at a specific test.

# update_test_data.py

This test mechanism does not call validate_upload.py, instead instantiating uploads for each example directory's upload data directly. It updates files by default (to prevent this behavior, pass the `--dry_run` flag, possibly in combination with `--verbose` for more detailed output).

To update fixture data, run the following, specifying individual example directories or any/all of the following: "examples/dataset-examples", "examples/dataset-iec-examples", "examples/tsv-examples".

Here is an example command that would update all README.md and fixtures.json files in `examples/dataset-examples`:

```
env PYTHONPATH=/ingest-validation-tools python -m tests_manual.update_test_data -t "examples/dataset-examples" --globus_token <globus_token>
```

Run the following command for more comprehensive documentation:

```
env PYTHONPATH=/ingest-validation-tools python -m tests_manual.update_test_data --help
```

## Manual Testing for Plugins

Plugins live in [https://github.com/hubmapconsortium/ingest-validation-tests](https://github.com/hubmapconsortium/ingest-validation-tests), requiring them to be tested manually rather than being added to automatic testing suite. To test plugins, first make sure you have [ingest-validation-tests properly installed](https://github.com/hubmapconsortium/ingest-validation-tools#running-plugin-tests).

Then, run the following from the top-level directory:

# ./tests-manual/test-plugins.sh

## Creating Tests

All examples with CEDAR API validation will need a README_ONLINE.md file. The test script will try to detect whether this file is missing based on example names including the string "cedar," but may not be 100% reliable.
