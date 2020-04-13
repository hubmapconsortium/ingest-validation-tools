from csv import DictReader
from pathlib import Path
from datetime import datetime
import re
from collections import defaultdict

from ingest_validation_tools.validation_utils import (
    get_metadata_tsv_errors,
    get_data_dir_errors
)


def _get_directory_type_from_path(path):
    return re.match(r'(.*)-metadata\.tsv$', Path(path).name)[1]


class Submission:
    def __init__(self, directory_path=None, override_tsv_paths={},
                 add_notes=True):
        self.directory_path = directory_path
        unsorted_effective_tsv_paths = (
            override_tsv_paths if override_tsv_paths
            else {
                _get_directory_type_from_path(path): path
                for path in directory_path.glob('*-metadata.tsv')
            }
        )
        self.effective_tsv_paths = {
            k: unsorted_effective_tsv_paths[k]
            for k in sorted(unsorted_effective_tsv_paths.keys())
        }
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
        types_paths = self.effective_tsv_paths.items()
        if not types_paths:
            errors['Missing'] = 'There are no effective TSVs.'
        for type, path in types_paths:
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
            rows = list(DictReader(f, dialect='excel-tab'))
            if not rows:
                errors['Warning'] = f'File has no data rows.'
            if self.directory_path:
                for i, row in enumerate(rows):
                    full_data_path = self.directory_path / row['data_path']
                    data_dir_errors = self._get_data_dir_errors(
                        type, full_data_path)
                    if data_dir_errors:
                        errors[f'{path.name} (row {i+2})'] = data_dir_errors
        return errors

    def _get_data_dir_errors(self, type, path):
        return get_data_dir_errors(type, path)

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
        referenced_data_paths = set(self._get_data_references().keys())
        non_metadata_paths = {
            path.name for path in self.directory_path.iterdir()
            if not path.name.endswith('-metadata.tsv')
        }
        unreferenced_paths = non_metadata_paths - referenced_data_paths
        return [str(path) for path in unreferenced_paths]

    def _get_multi_ref_errors(self):
        errors = {}
        data_references = self._get_data_references()
        for path, references in data_references.items():
            if len(references) > 1:
                errors[path] = references
        return errors

    def _get_data_references(self):
        # TODO: Move this to __init__
        data_references = defaultdict(list)
        for tsv_path in self.effective_tsv_paths.values():
            with open(tsv_path) as f:
                for i, row in enumerate(DictReader(f, dialect='excel-tab')):
                    reference = f'{tsv_path} (row {i+2})'
                    data_references[row['data_path']].append(reference)
        return data_references
