# Examples

The interface isn't finalized: For now there is a CLI,
but these examples will use a Python interface, to make testing easier.

Both the CLI and the python interface take two arguments:
- a submission directory to validate,
- and the type of the submission.

If the directory has the correct structure, you get a success, ie 0, status from the CLI:
```
>>> import validate
>>> validate._print_message('../tests/fixtures/codex-akoya/', 'codex-akoya')
0

```

If the directory doesn't have the right structure, you'll get an error message:
```
>>> validate._print_message('../tests/fixtures/almost-empty/', 'codex-akoya')
This item:
.
    place-holder.txt
.
should be one of these:
.
    - metadata_tsv
    - directory
.
This directory:
.
    place-holder.txt
.
should contain:
.
    metadata_tsv
.
1

```
