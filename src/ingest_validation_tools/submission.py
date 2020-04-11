import csv
from pathlib import Path
from datetime import datetime

from .validator import (
    get_metadata_tsv_errors
)


def _get_type_from_path(path):
    return re.match(r'(.+)-metadata\.tsv$', Path(tsv_path).name)[1]


class Submission:
    def __init__(self, directory_path=None, override_tsv_paths={},
            add_notes=True):
        self.directory_path = directory_path
        self.effective_tsv_paths = (
            override_tsv_paths if override_tsv_paths
            else {
                _get_type_from_path(path): path
                for path in directory_path.glob('*-metadata.tsv')
            }
        )
        self.add_notes = add_notes

    def get_errors(self):
        # This creates a deeply nested dict.
        # Keys are present only if there is actually an error to report.
        errors = {}
        tsv_errors = self._get_tsv_errors()
        reference_errors = self._get_reference_errors()
        if tsv_errors:
            errors['Metadata TSV Errors'] = tsv_errors
        if reference_errors:
            errors['Reference Errors'] = reference_errors
        if errors and self.add_notes:
            errors['Notes'] = {
                'Time': datetime.now(),
                'Directory': str(self.directory_path),
                'Effective TSVs': {
                    type: str(path) for type, path
                    in self.effective_tsv_paths.items()
                }
            }
        return errors

    def _get_tsv_errors(self):
        errors = {}
        for type, path in self.effective_tsv_paths.items():
            single_tsv_internal_errors = \
                self._get_single_tsv_internal_errors(type, path)
            single_tsv_external_errors = \
                self._get_single_tsv_external_errors(type, path)
            single_tsv_errors = {}
            if single_tsv_internal_errors:
                single_tsv_errors['Internal'] = single_tsv_internal_errors
            if single_tsv_external_errors:
                single_tsv_errors['External'] = single_tsv_external_errors
            if single_tsv_errors:
                errors[f'{path} (as {type})'] = single_tsv_errors
        return errors

    def _get_single_tsv_internal_errors(self, type, path):
        return get_metadata_tsv_errors(type=type, metadata_path=path)

    def _get_single_tsv_external_errors(self, type, path):
        errors = {}
        with open(path) as f:
            rows = list(csv.DictReader(f, dialect='excel-tab'))
            if not rows:
                errors[path.name] = f'{path} is empty'
            if self.directory_path:
                for i, row in enumerate(rows):
                    full_data_path = self.directory_path / row['data_path']
                    data_dir_errors = self._get_data_dir_errors(
                        type, full_data_path)
                    if data_dir_errors:
                        errors[f'{path.name} (row {i+1})'] = data_dir_errors
        return errors

    def _get_data_dir_errors(self, type, path):
        return 'TODO'

    def _get_reference_errors(self):
        errors = {}
        no_ref_errors = self._get_no_ref_errors()
        multi_ref_errors = self._get_multi_ref_errors()
        if no_ref_errors:
            errors['No References'] = no_ref_errors
        if multi_ref_errors:
            errors['Multiple References'] = multi_ref_errors
        return errors

    def _get_no_ref_errors(self):
        return 'TODO'

    def _get_multi_ref_errors(self):
        return 'TODO'
