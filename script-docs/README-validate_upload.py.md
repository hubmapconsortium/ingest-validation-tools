```text
usage: validate_upload.py [-h] --local_directory PATH
                          [--optional_fields FIELD [FIELD ...]] [--offline]
                          [--clear_cache] [--ignore_deprecation]
                          [--dataset_ignore_globs GLOB [GLOB ...]]
                          [--upload_ignore_globs GLOB [GLOB ...]]
                          [--encoding ENCODING]
                          [--plugin_directory PLUGIN_DIRECTORY]
                          [--globus_token GLOBUS_TOKEN]
                          [--cedar_api_key CEDAR_API_KEY]
                          [--output {as_md,as_text,as_text_list,as_yaml}]
                          [--add_notes] [--save_report]

Validate a HuBMAP upload, both the metadata TSVs and the datasets.
If you only want to validate a TSV in isolation, look at validate_tsv.py.

optional arguments:
  -h, --help            show this help message and exit
  --local_directory PATH
                        Local directory to validate
  --optional_fields FIELD [FIELD ...]
                        The listed fields will be treated as optional. (But if
                        they are supplied in the TSV, they will be validated.)
  --offline             Skip checks that require network access.
  --clear_cache         Clear cache of network check responses.
  --ignore_deprecation  Allow validation against deprecated versions of
                        metadata schemas.
  --dataset_ignore_globs GLOB [GLOB ...]
                        Matching files in each dataset directory will be
                        ignored. Default: .*
  --upload_ignore_globs GLOB [GLOB ...]
                        Matching files and subdirectories in the upload will
                        be ignored.
  --encoding ENCODING   Character-encoding to use for parsing TSVs. Default:
                        ascii. Work-in-progress:
                        https://github.com/hubmapconsortium/ingest-validation-
                        tools/issues/494
  --plugin_directory PLUGIN_DIRECTORY
                        Directory of plugin tests.
  --globus_token GLOBUS_TOKEN
                        Token for URL checking using Entity API.
  --cedar_api_key CEDAR_API_KEY
                        CEDAR Metadata Spreadsheet Validator API key.
  --output {as_md,as_text,as_text_list,as_yaml}
  --add_notes           Append a context note to error reports.
  --save_report         Save the report; Adding "--upload_ignore_globs
                        'report-*.txt'" is necessary to revalidate.

Typical usage:
  --local_directory: Used by lab before upload, and on Globus after upload.

  --local_directory + --dataset_ignore_globs + --upload_ignore_globs:
  After the initial validation on Globus, the metadata TSVs are broken up,
  and one-line TSVs are put in each dataset directory. This structure needs
  extra parameters.

Exit status codes:
  0: Validation passed
  1: Unexpected bug
  2: User error
  3: Validation failed
```
