# Examples

The interface isn't finalized: For now there is a CLI,
but the examples in this directory will use a Python interface,
to make testing easier.

Both the CLI and the python interface take two arguments:
- a submission directory to validate,
- and the type of the submission.

Each `.doctest` file in this directory validates the corresponding directory.
The periods sitting alone will not be there in the final release.
The number at the very end the exit code:
"0" means the directory is valid;
anything else means the directory is invalid.
