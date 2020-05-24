from ingest_validation_tools.directory_validator.globs_validator import (
    validate as glob_validate
)


def validate(path, spec_dict, dataset_ignore_globs=[]):
    return glob_validate(path, spec_dict, dataset_ignore_globs)
