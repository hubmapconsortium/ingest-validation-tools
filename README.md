# ingest-validation-tools
HuBMAP data submission guidelines,
and tools which check that submissions adhere to those guidelines.

## For data submitters and curators:

Checkout the repo and install dependencies:
```
python --version  # Should be Python3.
git clone https://github.com/hubmapconsortium/ingest-validation-tools.git
cd ingest-validation-tools
# Optionally, set up venv or conda, then:
pip install -r requirements.txt
src/validate_submission.py --help
```

You should see [the documention for `validate_submission.py`](README-validate_submission.py.md)

Now run it against one of the included examples, giving the type (`codex`) and the path to a TSV.
```
src/validate_submission.py --type_metadata codex \
  dataset-examples/bad-tsv-formats/submission/codex-akoya-metadata.tsv
```

You should now see [this (extensive) error message](dataset-examples/bad-tsv-formats/README.md).
This example TSV has been constructed with a mistake in every column, just to demonstrate the checks which are available. Hopefully, more often your experience will be like this:
```
src/validate_submission.py --type_metadata codex \
  dataset-examples/good-codex-akoya/submission/codex-akoya-metadata.tsv
```
```
No errors!
```

Documentation and metadata TSV templates for each assay type are [here](docs).

## For developers:

A good example is of usage is `validate-submission.py`; In a nutshell:
```python
submission = Submission(directory_path=path)
report = ErrorReport(submission.get_errors())
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

## Looking ahead: Submission directory validation

This repo already has code to validate the directory structure of submissions,
but we need to clarify what the directory structure actually is for each assay type.

Submissions are based on Globus directories containing:
- one or more `<type>-metadata.tsv` files.
- top-level subdirectories, or single files, in a 1-to-1 relationship with the rows of the TSVs.

The `data_path` and `metadata_path` in the TSV are relative to the location of the TSV.

[![Submission diagram](https://docs.google.com/drawings/d/e/2PACX-1vSQtvCCHf_t0SwpmlCINcwanq-dimJrkP93sm5E584bcL5iVy0t95W-HQz-dPGvbd46yRrnBVH8AAKF/pub?w=500)](https://docs.google.com/drawings/d/1J6sGrJcnm7W7E1MJczPiGeFGAlHob7RKJOwgKKrBrc8/edit)
