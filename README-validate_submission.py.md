```
usage: validate_submission.py [-h]
                              [--local_directory PATH | --tsv_paths PATH [PATH ...]]
                              [--optional_fields FIELD [FIELD ...]]
                              [--offline OFFLINE]
                              [--dataset_ignore_globs GLOB [GLOB ...]]
                              [--submission_ignore_globs GLOB [GLOB ...]]
                              [--encoding ENCODING]
                              [--plugin_directory PLUGIN_DIRECTORY]
                              [--output {as_browser,as_html_doc,as_html_fragment,as_md,as_text,as_text_list,as_yaml}]
                              [--add_notes]

Validate a HuBMAP submission, both the metadata TSVs, and the datasets,
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
  --offline OFFLINE     Skip checks that require network access.
  --dataset_ignore_globs GLOB [GLOB ...]
                        Matching files in each dataset directory will be
                        ignored. Default: .*
  --submission_ignore_globs GLOB [GLOB ...]
                        Matching sub-directories in the submission will be
                        ignored.
  --encoding ENCODING   Character-encoding to use for parsing TSVs. Default:
                        ascii. Work-in-progress:
                        https://github.com/hubmapconsortium/ingest-validation-
                        tools/issues/494
  --plugin_directory PLUGIN_DIRECTORY
                        Directory of plugin tests.
  --output {as_browser,as_html_doc,as_html_fragment,as_md,as_text,as_text_list,as_yaml}
  --add_notes           Append a context note to error reports.

Typical usecases:
  --tsv_paths: Used to validate TSVs in isolation, without checking references.

  --local_directory: Used in development against test fixtures, and could be used
  by labs before submission.

  --local_directory + --dataset_ignore_globs + --submission_ignore_globs:
  Currently, during ingest, the metadata TSVs are broken up, and one-line TSVs
  are put in each dataset directory. This structure needs extra ignores.
```
