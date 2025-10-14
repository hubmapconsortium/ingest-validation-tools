# ingest-validation-tools

HuBMAP data upload guidelines and instructions for checking that uploads adhere to those guidelines.
Assay documentation is on [Github Pages](https://hubmapconsortium.github.io/ingest-validation-tools/current).

HuBMAP has three distinct metadata processes:

- **Donor** metadata is handled by Jonathan Silverstein on an adhoc basis: He works with whatever format the TMC can provide, and aligns it with controlled vocabularies.
- **Sample** metadata is ingested by the [HuBMAP Data Ingest Portal](https://ingest.hubmapconsortium.org/)--see "Upload Sample Metadata" at the top of the page.
- **Dataset** uploads should be validated first by the TMCs. Dataset upload validation is the focus of this repo. [Details below.](#for-data-submitters-and-curators)

## For assay type working groups

Before we can write code to validate a particular assay type, there are some prerequisites:

- A document describing the experimental techniques involved.
- A list of the metadata fields for this type, along with descriptions and constraints.
- A list of the files to be expected in each dataset directory, along with descriptions.
  [Suggestions for describing directories](HOWTO-describe-directories.md).

When all the parts are finalized:

- The list of fields will be translated into a table schema.
- The list of files will be translated into a directory schema.

Examples of this translation can be found at the links to individual assay types on the [Current Schemas page](https://hubmapconsortium.github.io/ingest-validation-tools/current).

### Stability

Once approved, both the CEDAR Metadata Template (metadata schema)
and the list of files (directory schema) are fixed in a particular version.
The metadata for a particular assay type needs to be consistent for all datasets,
as does the set of files which comprise a dataset.
Edits to descriptions are welcome, as are improved validations.

If a more significant change is necessary, a new version is required,
and when the older form is no longer acceptable, the schema should be deprecated.

HuBMAP HIVE members: For questions about the stability of metadata,
contact Nils Gehlenborg (@ngehlenborg), or add him as a reviewer on the PR.
For the stability of directory structures,
contact Phil Blood (@pdblood).


## For data submitters and curators

### Upload process and upload directory structure

Data upload to HuBMAP is composed of discrete phases:

- Data provider prepares an upload:
    - Validate metadata files using the [HuBMAP Metadata Spreadsheet Validator](https://metadatavalidator.metadatacenter.org/)
    - Check that directory schemas match [requirements for assay type](https://hubmapconsortium.github.io/ingest-validation-tools/current)
- Data upload and validation
- Reorganization of bulk data upload into individual datasets
- Re-validation of individual datasets and pipeline runs

[![Data submission process](https://docs.hubmapconsortium.org/data-submission/)

Uploads are based on directories containing at a minimum:

- one or more `*-metadata.tsv` files.
- top-level dataset directories in a 1-to-1 relationship with the rows of the TSVs.

The type of a metadata TSV is determined by reading the first row.

The `antibodies_path` (for applicable types), `contributors_path`, and `data_path` are relative to the location of the TSV.
The antibodies and contributors TSV will typically be at the top level of the upload,
but if they are applicable to only a single dataset, they can be placed within that dataset's `extras/` directory.

[![Upload directory structure](https://docs.google.com/drawings/d/e/2PACX-1vS8F78bk0zHSRygMIyTLruAMxjL4c5EY_q_Mp3gN2TbdZLtalax5AxyvwBWyqWwAJH941ziqJPqBDTW/pub?w=500)](https://docs.google.com/drawings/d/1nhrRWBgcZh6GE2MCKysIq4KzsRL6SZm0jYtvadF83Kk/edit)

### Validation

To validate your metadata TSV files, use the [HuBMAP Metadata Spreadsheet Validator](https://metadatavalidator.metadatacenter.org/). This tool is a web-based application that will categorize any errors in your spreadsheet and provide help fixing those errors. More detailed instructions about using the tool can be found in the [Spreadsheet Validator Documentation](https://metadatacenter.github.io/spreadsheet-validator-docs/).

Documentation and metadata TSV templates for each assay type are [here](https://hubmapconsortium.github.io/ingest-validation-tools/).


## For developers and contributors

An example of the core error-reporting functionality:

```
python
upload = Upload(directory_path=path)
report = ErrorReport(upload)
print(report.as_text())
```

To make contributions, checkout the project, cd, venv, and then:

```
pip install -r requirements.txt
pip install -r requirements-dev.txt
brew install parallel    # On macOS
apt-get install parallel # On Ubuntu
./test.sh
```

After making tweaks to a schema, you will need to regenerate the docs. The test error message will tell you what to do.

### GitHub Actions

This repo uses GitHub Actions to check formatting and linting of code using black, isort, and flake8. Especially before submitting a PR, make sure your code is compliant per the versions specified in `requirements-dev.in`. Run the following from the base `ingest-validation-tools` directory:

```
black --line-length 99 .
isort --profile black --multi-line 3 .
flake8
```

Integrating [black](https://black.readthedocs.io/en/stable/integrations/editors.html) and potentially [isort](https://pycqa.github.io/isort/)/[flake8](https://flake8.pycqa.org/en/latest/index.html) with your editor may allow you to skip this step.

### Releases

For releases we're just using git tags:

```
$ git tag v0.0.x
$ git push origin v0.0.x
```

### Repo structure

[![Repo structure](https://docs.google.com/drawings/d/e/2PACX-1vQ8gorGI8ceYBf0bIJQlw4HvI3ooVTvCfickHhCvGJU4yy5kViJI39oqQ7xB20WLYxv8FMRuBLGwmH-/pub?w=600)](https://docs.google.com/drawings/d/1UK81oUHTSHetGXRsA-YeSFS-kb6Nw2rNpnw8SBysYXU/edit)

Checking in the built documentation is not the typical approach, but has worked well for this project:

- It's a sanity check when making schema changes. Since the schema for an assay actually comes for multiple sources, having the result of include resolution checked in makes it possible to catch unintended changes.
- It simplifies administration, since a separate static documentation site is not required.
- It enables easy review of the history of a schema, since the usual git/github tools can be used.

