```text
usage: validate_upload.py [-h] --local_directory PATH [--offline_only]
                          [--ignore_deprecation]
                          [--dataset_ignore_globs GLOB [GLOB ...]]
                          [--upload_ignore_globs GLOB [GLOB ...]]
                          [--encoding ENCODING]
                          [--plugin_directory PLUGIN_DIRECTORY]
                          [--run_plugins] [--globus_token GLOBUS_TOKEN]
                          [--output {as_md,as_text,as_text_list,as_yaml}]

Validate a HuBMAP upload, both the metadata TSVs and the datasets.

optional arguments:
  -h, --help            show this help message and exit
  --local_directory PATH
                        Local directory to validate
  --offline_only        Skip URL checks (Spreadsheet Validator API checks
                        still run).
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
  --run_plugins         Run plugin validation even if there are upstream
                        errors.
  --globus_token GLOBUS_TOKEN
                        Token for URL checking using Entity API.
  --output {as_md,as_text,as_text_list,as_yaml}

Exit status codes:
  0: Validation passed
  1: Unexpected bug
  2: User error
  3: Validation failed
```
