# `examples/`

This directory contains example inputs and outputs of different components of this system. Before adding new example directories, consider whether Python unittests would be a better solution.

For instructions about how to run tests, please see `tests/README.md`.

## `dataset-examples/`

The core of `ingest-validation-tools` is dataset upload validation.
Each subdirectory here is an end-to-end test of upload validation. Each contains:

- an `upload` directory, containing one or more metadata TSVs, dataset directories, and contributors and antibodies TSVs,
- a `fixtures.json` file, containing responses from the assayclassifier endpoint and Spreadsheet Validator that are used as fixture data in offline testing,
- and a `README.md` with the output when validating that directory.

Examples which are expected to produce errors are prefixed with `bad-`, those that are good, `good-`.

## `dataset-iec-examples/`

After upload, TSVs are split up, and directory structures are re-arranged.
These structures can still be validated, but it takes a slightly different set of options,
and those options are tested here.

## `plugin-tests`

Plugins are turned off by default for testing, as they require an additional repo: [ingest-validation-tests](https://github.com/hubmapconsortium/ingest-validation-tests). See [tests/manual/README.md](tests/manual/README.md) for more information about plugin tests.
