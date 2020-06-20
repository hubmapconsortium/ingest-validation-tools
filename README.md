# ingest-validation-tools
HuBMAP data submission guidelines,
and tools which check that submissions adhere to those guidelines.

## HuBMAP submission structure:

Submissions are based on Globus directories containing:
- one or more `<type>-metadata.tsv` files.
- top-level subdirectories, or single files, in a 1-to-1 relationship with the rows of the TSVs.

The `data_path` and `metadata_path` in the TSV are relative to the location of the TSV.

[![Submission diagram](https://docs.google.com/drawings/d/e/2PACX-1vSQtvCCHf_t0SwpmlCINcwanq-dimJrkP93sm5E584bcL5iVy0t95W-HQz-dPGvbd46yRrnBVH8AAKF/pub?w=359&amp;h=383)](https://docs.google.com/drawings/d/1J6sGrJcnm7W7E1MJczPiGeFGAlHob7RKJOwgKKrBrc8/edit)

## For data submitters:

Documentation and metadata TSV templates are [here](docs).

## For API users:

Right now, this isn't actually being packaged, but if that would be useful, please file an issue.
A good example is `validate-submission.py`, but in a nutshell you'll do something like:
```python
submission = Submission(directory_path=path)
report = ErrorReport(submission.get_errors())
print(report.as_text())
```

## For curators:

Example submissions and validation reports are [here](dataset-examples).

You can [run validation locally](README-validate_submission.md)
before the same checks are run automatically during ingest.

## For developers:

Checkout the project, cd, venv, and then:
```
pip install -r requirements.txt
pip install -r requirements-dev.txt
./test.sh
```

After making tweaks to the schema, you can
[regenerate the docs](README-generate_dataset_docs.py.md).

For releases we're just using git tags:
```
$ git tag v0.0.x
$ git push origin v0.0.x
```

... and update the CHANGELOG.md.

## Big picture:

Our goal is to be able to run the same quick validations locally, and as part of the ingest-pipeline.

[![Flow diagram](https://docs.google.com/drawings/d/e/2PACX-1vQ7_q4K-JmAjGSMyA4Q5-3094B26fD4opW3s3jzbLHvXp4IsoEpt7fwXHYvW7ZQhQKSSTPF7zc5VoEI/pub?w=775&h=704)](https://docs.google.com/drawings/d/1A5irNDqfnyH8zzDiB6Vs0_WwUWByl7XJyjd2x82DlXk/edit)
