from ingest_validation_tools.validation_utils import (
    get_tsv_errors
)


class Samples:
    def __init__(self, path=None):
        self.path = path

    def get_errors(self):
        # This creates a deeply nested dict.
        # Keys are present only if there is actually an error to report.
        errors = {}
        tsv_errors = get_tsv_errors(self.path, type='sample')
        if tsv_errors:
            errors['Sample TSV Errors'] = tsv_errors
        return errors
