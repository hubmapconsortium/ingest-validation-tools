# ingest-validation-tools
HuBMAP data upload guidelines, and tools which check that uploads adhere to those guidelines.
Assay documenentation is on [Github Pages](https://hubmapconsortium.github.io/ingest-validation-tools/).

## For assay type working groups:

Before we can write code to validate a particular assay type, there are some prequisites:
- A document describing the experimental techniques involved.
- A list of the metadata fields for this type, along with descriptions and constraints.
- A list of the files to be expected in each dataset directory, along with descriptions.
  [Suggestions for describing directories](HOWTO-describe-directories.md).

When all the parts are finalized,
- The document will be translated into markdown, and added [here](https://github.com/hubmapconsortium/portal-docs/tree/master/assays).
- The list of fields will be translated into a table schema, like those [here](src/ingest_validation_tools/table-schemas).
- The list of files will be translated into a directory schema, like those [here](src/ingest_validation_tools/directory-schemas).

### Stability

Once approved, both the list of metadata fields and the list of files is fixed.
The metadata for a particular assay type needs to be consistent for all datasets,
as does the set of files which comprise a dataset.
Edits to descriptions are welcome, as are improved validations.

HuBMAP HIVE members: For questions about the stability of metadata,
contact Nils Gehlenborg (@ngehlenborg), or add him as a reviewer on the PR.
For the stability of directory structures,
contact Phil Blood (@pdblood).

## For data submitters and curators:

Checkout the repo and install dependencies:
```
python --version  # Should be Python3.
git clone https://github.com/hubmapconsortium/ingest-validation-tools.git
cd ingest-validation-tools
# Optionally, set up venv or conda, then:
pip install -r requirements.txt
src/validate_upload.py --help
```

You should see [the documention for `validate_upload.py`](script-docs/README-validate_upload.py.md)

Now run it against one of the included examples, giving the path to an upload directory:
```
src/validate_upload.py --local_directory examples/dataset-examples/bad-tsv-formats/upload --output as_text
```

You should now see [this (extensive) error message](examples/dataset-examples/bad-tsv-formats/README.md).
This example TSV has been constructed with a mistake in every column, just to demonstrate the checks which are available. Hopefully, more often your experience will be like this:
```
src/validate_upload.py --local_directory examples/dataset-examples/good-codex-akoya/upload
```
```
No errors!
```

Documentation and metadata TSV templates for each assay type are [here](https://hubmapconsortium.github.io/ingest-validation-tools/).
Addition help for certain common error messages is available [here](README-validate-upload-help.md)

### Validating single TSVs:

If you don't have an entire upload directory at hand, you can validate individual
metadata, antibodies, contributors, or sample TSVs:
```
src/validate_tsv.py --schema metadata --path examples/dataset-examples/good-scatacseq-v1/upload/metadata.tsv
```
```
No errors!
```

### Running plugin tests:

Additional plugin tests can also be run.
These additional tests confirm that the files themselves are valid, not just that the directory structures are correct.
These additional tests are in a separate repo, and have their own dependencies.

```
# Starting from ingest-validation-tools...
cd ..
git clone https://github.com/hubmapconsortium/ingest-validation-tests.git
cd ingest-validation-tests
pip install -r requirements.txt

# Back to ingest-validation-tools...
cd ../ingest-validation-tools
src/validate_upload.py --local_directory examples/dataset-examples/good-codex-akoya/upload \
  --plugin_directory ../ingest-validation-tests/src/ingest_validation_tests/
```

## For developers:

A good example is of usage is `validate-upload.py`; In a nutshell:
```python
upload = Upload(directory_path=path)
report = ErrorReport(upload.get_errors())
print(report.as_text())
```
(If it would be useful for this to be installable with `pip`, please file an issue.)

## For contributors:

Checkout the project, cd, venv, and then:
```
pip install -r requirements.txt
pip install -r requirements-dev.txt
./test.sh
```

After making tweaks to the schema, you will need to regenerate the docs:
The test error message will tell you what to do.

For releases we're just using git tags:
```
$ git tag v0.0.x
$ git push origin v0.0.x
```

## Repo structure
[![Repo structure](https://docs.google.com/drawings/d/e/2PACX-1vQ8gorGI8ceYBf0bIJQlw4HvI3ooVTvCfickHhCvGJU4yy5kViJI39oqQ7xB20WLYxv8FMRuBLGwmH-/pub?w=600)](https://docs.google.com/drawings/d/1UK81oUHTSHetGXRsA-YeSFS-kb6Nw2rNpnw8SBysYXU/edit)

Checking in the built documentation is not the typical approach, but has worked well for this project:
- It's a sanity check when making schema changes. Since the schema for an assay actually comes for multiple sources, having the result of include resolution checked in makes it possible to catch unintended changes.
- It simplifies administration, since a separate static documentation site is not required.
- It enables easy review of the history of a schema, since the usual git/github tools can be used.

## Upload process and upload directory structure

Data upload to HuBMAP is composed of discrete phases:
- Upload preparation and validation
- Upload and re-validation
- Restructuring
- Re-re-validation and pipeline runs

[![Upload process](https://docs.google.com/drawings/d/e/2PACX-1vScOVTJCQjaHj0oiVuvPxuQDNXFCtI-CGTTOm-kSPji9DehMxRIaWg98qKAkkvwSWn5d2TuL1z4mIyh/pub?w=1000)](https://docs.google.com/drawings/d/11DLkPe_mfC3kh69HCYqCx5MAVTTkYOXqVjyFY85jMLQ/edit)

Uploads are based on directories containing at a minimum:
- one or more `*-metadata.tsv` files.
- top-level dataset directories in a 1-to-1 relationship with the rows of the TSVs.

The type of a metadata TSV is determined by reading the first row.

The `antibodies_path` (for applicable types), `contributors_path`, and `data_path` are relative to the location of the TSV.
The antibodies and contributors TSV will typically be at the top level of the upload,
but if they are applicable to only a single dataset, they can be placed within that dataset's `extras/` directory.

You can validate your upload directory locally, then upload it to Globus, and the same validation will be run there.

[![Upload diagram](https://docs.google.com/drawings/d/e/2PACX-1vS8F78bk0zHSRygMIyTLruAMxjL4c5EY_q_Mp3gN2TbdZLtalax5AxyvwBWyqWwAJH941ziqJPqBDTW/pub?w=500)](https://docs.google.com/drawings/d/1nhrRWBgcZh6GE2MCKysIq4KzsRL6SZm0jYtvadF83Kk/edit)
