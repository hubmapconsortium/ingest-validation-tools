# `examples/`

Validation is run offline by the tests in the `tests` directory. Online validation can be run manually; see [tests/manual/README.md](tests/manual/README.md).

This directory contains example inputs and outputs of different components of this system.
Adding more examples is one way to test new schemas or new code...
but it's possible to have too much of a good thing:
If we eventually _do_ need to change the behavior,
sorting out redundant failing tests can be a nuisance.
Particularly when testing new code, granular unit tests can give you more information than coarse end-to-end tests.

Putting that aside, here is what we have:

## `custom-constraint-examples/`
# DEPRECATED

We've added a number of extensions to the base TSV validation we get from
[Frictionless Table Schemas](https://specs.frictionlessdata.io/table-schema/).
Each subdirectory contains a `schema.yaml` that exercises one extension,
an `input.tsv` to validate, and an `output.txt` with the error message produced.

## `dataset-examples/`

The core of `ingest-validation-tools` is dataset upload validation.
Each subdirectory here is an end-to-end test of upload validation. Each contains:

- an `upload` directory, containing one or more metadata TSVs, dataset directories, and contributors and antibodies TSVs,
- a `fixtures.json` file, containing responses from the assayclassifier endpoint and Spreadsheet Validator that are used as fixture data in offline testing,
- and a `README.md` with the output when validating that directory.

Examples which are expected to produce errors are prefixed with `bad-`, those that are good, `good-`.

To add a new test:
- Create a new subdirectory with a `good-` or `bad-` name and add your `upload` subdirectory.
- Run the following command to create the `README.md` and `fixtures.json` files:

```
env PYTHONPATH=/ingest-validation-tools python -m tests.manual.update_test_data -t examples/<path_to_your_example_dir>/upload --globus_token <globus_token>
```

Note: You can find your personal Globus token by logging in to a site that requires Globus authentication (e.g. https://ingest.hubmapconsortium.org/) and looking at the Authorization header for your request in the Network tab of your browser. Omit the "Bearer " prefix.
- Make sure the result makes sense! The software can tell you what the result of validation is, but it can't know whether that result is actually correct.

## `dataset-iec-examples/`

After upload, TSVs are split up, and directory structures are re-arranged.
These structures can still be validated, but it takes a slightly different set of options,
and those options are tested here.

## `plugin-tests`

Plugins are turned off by default for testing, as they require an additional repo: [ingest-validation-tests](https://github.com/hubmapconsortium/ingest-validation-tests). See [tests/manual/README.md](tests/manual/README.md) for more information about plugin tests.
