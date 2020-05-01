```
usage: validate_submission.py [-h]
                              [--local_directory PATH | --globus_url URL | --globus_origin_directory ORIGIN_PATH]
                              [--type_metadata TYPE_PATH [TYPE_PATH ...]]
                              [--optional_fields FIELD [FIELD ...]]
                              [--ignore_files FILE [FILE ...]]
                              [--output {as_browser,as_html,as_md,as_text,as_yaml}]
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
                        A list of type / metadata.tsv pairs of the form "<af|a
                        tacseq|codex|maldiims|scrnaseq|seqfish>:<local_path_to
                        _tsv>".
  --optional_fields FIELD [FIELD ...]
                        The listed fields will be treated as optional. (But if
                        they are supplied in the TSV, they will be validated.)
  --ignore_files FILE [FILE ...]
                        Files with these names at the top level of the
                        submission will be ignored.
  --output {as_browser,as_html,as_md,as_text,as_yaml}
  --add_notes           Append a context note to error reports.

Typical usecases:

  --type_metadata + --globus_url: Validate one or more
  local metadata.tsv files against a submission directory already on Globus.

  --globus_url: Validate a submission directory on Globus,
  with <type>-metadata.tsv files in place.

  --local_directory: Used in development against test fixtures, and in
  the ingest-pipeline, where Globus is the local filesystem.
```
