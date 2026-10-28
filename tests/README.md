# Testing

## Running tests

### Metadata validation of a single TSV

To check just the metadata for a single TSV, use the [Metadata Spreadsheet Validator](https://metadatavalidator.metadatacenter.org/).

### Automated testing

As a default behavior, testing (e.g. via GitHub action or by running `./test.sh`) does not hit the [CEDAR Metadata Center Spreadsheet Validator](https://metadatacenter.github.io/spreadsheet-validator-docs/api-reference/) or [assayclassifier](https://github.com/hubmapconsortium/ingest-api/tree/main/src/routes/assayclassifier) endpoint, nor does it perform any URL checking.

Running `./test.sh` will mimic the offline behavior of the GitHub action that runs on push and creation of PRs.

Additional flags are available to skip longer tests (linting/formatting and docs generation). Run this for help:

```
./test.sh --help
```

### Manual offline testing

Individual test files can be run as normal using the unittest framework:

```
python -m tests.test_single_tsv
python -m tests.test_dataset_examples TestUploads.test_info_reporting
```

To test a single example directory:

```
python -m tests.manual.manual_testing -t examples/dataset-iec-examples/bad-example
```

### Testing online / keeping fixture data current

Online testing will make all requests and will overwrite the fixtures.json files for example datasets/uploads in the `examples/` directory.

Run all tests online with:

```
python -m tests.manual.manual_testing -o -g "<hubmap_globus_token>"
```

This will replace fixtures.json files but will not update README.json files. To automatically update all README.json files, run:

```
python -m tests.manual.manual_testing -o -g "<hubmap_globus_token>" -w
```

In either case, including `-t` followed by one or more example directory paths will update only those paths.

```
# Update fixtures but not readmes for target dir "dir_name1"
python -m tests.manual.manual_testing -t examples/dataset-examples/<dir_name1> -o -g "<hubmap_globus_token>"

# Update both for target dir "dir_name1"
python -m tests.manual.manual_testing -t examples/dataset-examples/<dir_name1> -o -g "<hubmap_globus_token>" -w
```

Note: You can find your personal Globus token by logging in to a site that requires Globus authentication (e.g. https://ingest.hubmapconsortium.org/) and looking at the Authorization header for your request in the Network tab of your browser. Omit the "Bearer" prefix.

### Plugin testing

Plugins live in [https://github.com/hubmapconsortium/ingest-validation-tests](https://github.com/hubmapconsortium/ingest-validation-tests), requiring them to be tested manually rather than being added to automatic testing suite. To test plugins, first make sure you have [ingest-validation-tests properly installed](https://github.com/hubmapconsortium/ingest-validation-tools#running-plugin-tests).

```
pip install -r <path_to_IVTests>/requirements.txt
```

To just run Python unittests for plugins, run the following from the top-level directory:

```
python tests/manual/test_plugins.py
```

You can run plugin tests online with:

```
python tests/manual/test_plugins.py -o -g "<globus_token>"
```

Include the `-w` flag to write new README.json files:

```
python tests/manual/test_plugins.py -o -g "<globus_token>" -w
```

## Creating Tests

All new examples will need fixtures.json and README.json files. After adding the test data to its own directory under the appropriate `examples/` subdirectory, run this to generate required files:

```
python -m tests.manual.manual_testing -t <new_example_dir_path> -o -g "<globus_token>"
```

Make sure the result makes sense! The software can tell you what the result of validation is, but it can't know whether that result is actually correct.

## Updating examples

Tests that find differences between fixtures and test output will give instructions about how to see more information and/or update fixtures/README.
