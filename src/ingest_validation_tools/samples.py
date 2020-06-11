from pathlib import Path

from yaml import safe_load as load_yaml
from goodtables import validate as validate_table

from ingest_validation_tools.validation_utils import (
    column_number_to_letters
)


class Samples:
    def __init__(self, path=None):
        self.path = path

    def get_errors(self):
        # This creates a deeply nested dict.
        # Keys are present only if there is actually an error to report.
        errors = {}
        tsv_errors = self._get_tsv_errors()
        if tsv_errors:
            errors['Sample TSV Errors'] = tsv_errors
        return errors

    def _get_tsv_errors(self):
        schema = load_yaml(
            (Path(__file__).parent / 'table-schemas' / 'samples.yaml').read_text()
        )
        report = validate_table(self.path, schema=schema,
                                format='csv', delimiter='\t',
                                skip_checks=['blank-row'])
        error_messages = report['warnings']
        # TODO: Factor out more of this as util.
        if 'tables' in report:
            for table in report['tables']:
                error_messages += [
                    column_number_to_letters(e['message'])
                    for e in table['errors']
                ]
        return error_messages
