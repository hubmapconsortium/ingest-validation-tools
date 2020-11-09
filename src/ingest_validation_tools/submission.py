from csv import DictReader
from pathlib import Path
from datetime import datetime
import re
from collections import defaultdict
from fnmatch import fnmatch

from ingest_validation_tools.validation_utils import (
    get_tsv_errors,
    get_data_dir_errors,
    get_contributors_errors
)

from ingest_validation_tools.plugin_validator import (
    run_plugin_validators_iter,
    ValidatorError as PluginValidatorError
)


def _get_directory_type_from_path(path):
    return re.match(r'(.*)-metadata\.tsv$', Path(path).name)[1]


def _get_tsv_rows(path):
    with open(path, encoding='latin-1') as f:
        rows = list(DictReader(f, dialect='excel-tab'))
    return rows


class Submission:
    def __init__(self, directory_path=None, override_tsv_paths={},
                 optional_fields=[], add_notes=True,
                 dataset_ignore_globs=[], submission_ignore_globs=[],
                 plugin_dir_abs_path=None):
        self.directory_path = directory_path
        self.optional_fields = optional_fields
        self.dataset_ignore_globs = dataset_ignore_globs
        self.submission_ignore_globs = submission_ignore_globs
        self.plugin_dir_abs_path = plugin_dir_abs_path
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
        if tsv_errors:
            errors['Metadata TSV Errors'] = tsv_errors

        reference_errors = self._get_reference_errors()
        if reference_errors:
            errors['Reference Errors'] = reference_errors

        plugin_errors = self._get_plugin_errors()
        if plugin_errors:
            errors['Plugin Errors'] = plugin_errors

        if self.add_notes:
            errors['Notes'] = {
                'Time': datetime.now(),
                'Directory': str(self.directory_path),
                'Effective TSVs': {
                    type: str(path) for type, path
                    in self.effective_tsv_paths.items()
                }
            }
        return errors

    def _get_plugin_errors(self):
        plugin_path = self.plugin_dir_abs_path
        if not plugin_path:
            return None
        errors = defaultdict(list)
        for metadata_path in self.effective_tsv_paths.values():
            try:
                for k, v in run_plugin_validators_iter(metadata_path,
                                                       plugin_path):
                    errors[k].append(v)
            except PluginValidatorError as e:
                errors['Unexpected Plugin Error'] = str(e)
        return {k: v for k, v in errors.items()}  # get rid of defaultdict

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
        return get_tsv_errors(
            type=type, tsv_path=path,
            optional_fields=self.optional_fields)

    def _get_single_tsv_external_errors(self, type, path):
        errors = {}
        rows = _get_tsv_rows(path)
        if not rows:
            errors['Warning'] = 'File has no data rows.'
        if self.directory_path:
            for i, row in enumerate(rows):
                row_number = f'row {i+2}'

                data_path = self.directory_path / \
                    row['data_path']
                data_dir_errors = self._get_data_dir_errors(
                    type, data_path)
                if data_dir_errors:
                    errors[f'{row_number}, referencing {data_path}'] = data_dir_errors

                contributors_path = self.directory_path / \
                    row['contributors_path']
                contributors_errors = self._get_contributors_errors(
                    contributors_path)
                if contributors_errors:
                    errors[f'{row_number}, contributors {contributors_path}'] = \
                        contributors_errors
        return errors

    def _get_data_dir_errors(self, type, data_path):
        return get_data_dir_errors(
            type, data_path, dataset_ignore_globs=self.dataset_ignore_globs)

    def _get_contributors_errors(self, contributors_path):
        return get_contributors_errors(contributors_path)

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
        if not self.directory_path:
            return {}
        referenced_data_paths = set(self._get_data_references().keys()) \
            | set(self._get_contributors_references().keys())
        non_metadata_paths = {
            path.name for path in self.directory_path.iterdir()
            if not path.name.endswith('-metadata.tsv')
            and not any([
                fnmatch(path.name, glob)
                for glob in self.submission_ignore_globs
            ])
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
        return self._get_references('data_path')

    def _get_contributors_references(self):
        return self._get_references('contributors_path')

    def _get_references(self, col_name):
        references = defaultdict(list)
        for tsv_path in self.effective_tsv_paths.values():
            for i, row in enumerate(_get_tsv_rows(tsv_path)):
                if col_name in row:
                    reference = f'{tsv_path} (row {i+2})'
                    references[row[col_name]].append(reference)
        return references
