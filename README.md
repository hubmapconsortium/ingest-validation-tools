# ingest-validation-tools
HuBMAP data submission guidelines,
and tools which check that submissions adhere to those guidelines.

## HuBMAP submission structure:

Submissions are based on Globus directories containing:
- one or more `<type>-metadata.tsv` files.
- top-level subdirectories, or single files, in a 1-to-1 relationship with the rows of the TSVs.

The `data_path` and `metadata_path` in the TSV are relative to the location of the TSV.

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

Example submissions and validation reports are [here](examples).

You can run validation locally before the same checks are run automatically during ingest:
```
usage: validate_submission.py [-h]
                              [--local_directory PATH | --globus_url URL | --globus_origin_directory ORIGIN_PATH]
                              [--type_metadata TYPE_PATH [TYPE_PATH ...]]
                              [--optional_fields FIELD [FIELD ...]]
                              [--ignore_files FILE [FILE ...]]
                              [--output {as_html_document,as_html_fragment,as_text,as_yaml}]
                              [--add_notes]

Validate a HuBMAP submission, both the metadata TSVs, and the datasets,
either local or remote, or a combination of the two.

optional arguments:
  -h, --help            show this help message and exit
  --local_directory PATH
                        Local directory to validate
  --globus_url URL      The Globus File Manager URL of a directory to
                        validate.
  --globus_origin_directory ORIGIN_PATH
                        A Globus submission directory to validate; Should have
                        the form "<globus_origin_id>:<globus_path>".
  --type_metadata TYPE_PATH [TYPE_PATH ...]
                        A list of type / metadata.tsv pairs of the form
                        "<atacseq|codex|seqfish>:<local_path_to_tsv>".
  --optional_fields FIELD [FIELD ...]
                        The listed fields will be treated as optional. (But if
                        they are supplied in the TSV, they will be validated.)
  --ignore_files FILE [FILE ...]
                        Files with these names at the top level of the
                        submission will be ignored.
  --output {as_html_document,as_html_fragment,as_text,as_yaml}
  --add_notes           Append a context note to error reports.

Typical usecases:

  --type_metadata + --globus_url: Validate one or more
  local metadata.tsv files against a submission directory already on Globus.

  --globus_url: Validate a submission directory on Globus,
  with <type>-metadata.tsv files in place.

  --local_directory: Used in development against test fixtures, and in
  the ingest-pipeline, where Globus is the local filesystem.
```

## For developers:

Checkout the project, cd, venv, and then:
```
pip install -r requirements.txt
pip install -r requirements-dev.txt
./test.sh
```

After making tweaks to the schema, you can regenerate the docs:

```
$ src/generate_docs.py -h
usage: generate_docs.py [-h] {atacseq,codex,seqfish} target

positional arguments:
  {atacseq,codex,seqfish}
                        What type to generate
  target                Directory to write output to

optional arguments:
  -h, --help            show this help message and exit
```

For releases we're just using git tags:
```
$ git tag v0.0.x
$ git push origin v0.0.x
```

... and update the CHANGELOG.md.

## Big picture:

Our goal is to be able to run the same quick validations locally, and as part of the ingest-pipeline.

[![Flow diagram](https://docs.google.com/drawings/d/e/2PACX-1vQ7_q4K-JmAjGSMyA4Q5-3094B26fD4opW3s3jzbLHvXp4IsoEpt7fwXHYvW7ZQhQKSSTPF7zc5VoEI/pub?w=775&h=704)](https://docs.google.com/drawings/d/1A5irNDqfnyH8zzDiB6Vs0_WwUWByl7XJyjd2x82DlXk/edit)
