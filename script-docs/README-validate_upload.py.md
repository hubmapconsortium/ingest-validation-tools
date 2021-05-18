```text
usage: validate_upload.py [-h]
                              (--local_directory PATH | --tsv_paths PATH [PATH ...])
                              [--optional_fields FIELD [FIELD ...]]
                              [--offline] [--clear_cache]
                              [--dataset_ignore_globs GLOB [GLOB ...]]
                              [--upload_ignore_globs GLOB [GLOB ...]]
                              [--encoding ENCODING]
                              [--plugin_directory PLUGIN_DIRECTORY]
                              [--output {as_browser,as_html_doc,as_html_fragment,as_md,as_text,as_text_list,as_yaml}]
                              [--add_notes]

Validate a HuBMAP upload, both the metadata TSVs, and the datasets,
either local or remote, or a combination of the two.

optional arguments:
  -h, --help            show this help message and exit
  --local_directory PATH
                        Local directory to validate
  --tsv_paths PATH [PATH ...]
                        Paths of metadata.tsv files.
  --optional_fields FIELD [FIELD ...]
                        The listed fields will be treated as optional. (But if
                        they are supplied in the TSV, they will be validated.)
  --offline             Skip checks that require network access.
  --clear_cache         Clear cache of network check responses.
  --dataset_ignore_globs GLOB [GLOB ...]
                        Matching files in each dataset directory will be
                        ignored. Default: .*
  --upload_ignore_globs GLOB [GLOB ...]
                        Matching sub-directories in the upload will be
                        ignored.
  --encoding ENCODING   Character-encoding to use for parsing TSVs. Default:
                        ascii. Work-in-progress:
                        https://github.com/hubmapconsortium/ingest-validation-
                        tools/issues/494
  --plugin_directory PLUGIN_DIRECTORY
                        Directory of plugin tests.
  --output {as_browser,as_html_doc,as_html_fragment,as_md,as_text,as_text_list,as_yaml}
  --add_notes           Append a context note to error reports.

Typical usage:
  --tsv_paths: Used to validate Sample metadata TSVs. (Because it does
  not check references, should not be used to validate Dataset metadata TSVs.)

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
