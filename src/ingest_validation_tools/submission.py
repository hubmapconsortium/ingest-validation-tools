from datetime import datetime
from collections import defaultdict
from fnmatch import fnmatch
from pathlib import Path
from collections import Counter

import requests

from ingest_validation_tools.yaml_include_loader import load_yaml

from ingest_validation_tools.validation_utils import (
    get_tsv_errors,
    get_data_dir_errors,
    get_contributors_errors,
    get_antibodies_errors,
    dict_reader_wrapper
)

from ingest_validation_tools.plugin_validator import (
    run_plugin_validators_iter,
    ValidatorError as PluginValidatorError
)


def _assay_name_to_code(name):
    '''
    Given an assay name, read all the schemas until one matches.
    '''
    for path in (Path(__file__).parent / 'table-schemas' / 'level-2').glob('*.yaml'):
        schema = load_yaml(path)
        for field in schema['fields']:
            if field['name'] == 'assay_type' and name in field['constraints']['enum']:
                return path.stem
    return None


TSV_SUFFIX = 'metadata.tsv'


class Submission:
    def __init__(self, directory_path=None, tsv_paths=[],
                 optional_fields=[], add_notes=True,
                 dataset_ignore_globs=[], submission_ignore_globs=[],
                 plugin_directory=None, encoding=None):
        self.directory_path = directory_path
        self.optional_fields = optional_fields
        self.dataset_ignore_globs = dataset_ignore_globs
        self.submission_ignore_globs = submission_ignore_globs
        self.plugin_directory = plugin_directory
        self.encoding = encoding
        unsorted_effective_tsv_paths = {
            str(path): self._get_type_from_first_line(path)
            for path in (
                tsv_paths if tsv_paths
                else directory_path.glob(f'*{TSV_SUFFIX}')
            )
        }
        self.effective_tsv_paths = {
            k: unsorted_effective_tsv_paths[k]
            for k in sorted(unsorted_effective_tsv_paths.keys())
        }
        self.add_notes = add_notes

    def _get_type_from_first_line(self, path):
        rows = dict_reader_wrapper(path, self.encoding)
        if not rows:
            return None
        name = rows[0]['assay_type']
        return _assay_name_to_code(name)

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
                'Effective TSVs': self.effective_tsv_paths
            }
        return errors

    def _get_plugin_errors(self):
        plugin_path = self.plugin_directory
        if not plugin_path:
            return None
        errors = defaultdict(list)
        for metadata_path in self.effective_tsv_paths.keys():
            try:
                for k, v in run_plugin_validators_iter(metadata_path,
                                                       plugin_path):
                    errors[k].append(v)
            except PluginValidatorError as e:
                # We are ok with just returning a single error, rather than all.
                errors['Unexpected Plugin Error'] = str(e)
        return dict(errors)  # get rid of defaultdict

    def _get_tsv_errors(self):
        if not self.effective_tsv_paths:
            return {'Missing': 'There are no effective TSVs.'}

        types_counter = Counter(self.effective_tsv_paths.values())
        repeated = [
            assay_type
            for assay_type, count in types_counter.items()
            if count > 1
        ]
        if repeated:
            return f'There is more than one TSV for this type: {", ".join(repeated)}'

        errors = {}
        for path, assay_type in self.effective_tsv_paths.items():
            single_tsv_internal_errors = \
                self._get_single_tsv_internal_errors(assay_type, path)
            single_tsv_external_errors = \
                self._get_single_tsv_external_errors(assay_type, path)
            single_tsv_errors = {}
            if single_tsv_internal_errors:
                single_tsv_errors['Internal'] = single_tsv_internal_errors
            if single_tsv_external_errors:
                single_tsv_errors['External'] = single_tsv_external_errors
            if single_tsv_errors:
                errors[f'{path} (as {assay_type})'] = single_tsv_errors
        return errors

    def _get_single_tsv_internal_errors(self, assay_type, path):
        return get_tsv_errors(
            type=assay_type, tsv_path=path,
            optional_fields=self.optional_fields)

    def _get_single_tsv_external_errors(self, assay_type, path):
        rows = dict_reader_wrapper(path, self.encoding)
        if not rows:
            return 'File has no data rows.'
        if 'data_path' not in rows[0] or 'contributors_path' not in rows[0]:
            return 'File is missing data_path or contributors_path.'
        if not self.directory_path:
            return None

        errors = {}
        status_of_doi = {}
        for i, row in enumerate(rows):
            row_number = f'row {i+2}'

            data_path = self.directory_path / \
                row['data_path']
            data_dir_errors = self._get_data_dir_errors(
                assay_type, data_path)
            if data_dir_errors:
                errors[f'{row_number}, referencing {data_path}'] = data_dir_errors

            contributors_path = self.directory_path / \
                row['contributors_path']
            contributors_errors = self._get_contributors_errors(
                contributors_path)
            if contributors_errors:
                errors[f'{row_number}, contributors {contributors_path}'] = \
                    contributors_errors

            if 'antibodies_path' in row:
                antibodies_path = self.directory_path / \
                    row['antibodies_path']
                antibodies_errors = self._get_antibodies_errors(
                    antibodies_path)
                if antibodies_errors:
                    errors[f'{row_number}, antibodies {antibodies_path}'] = \
                        antibodies_errors

            for k in row.keys():
                if not k.endswith('protocols_io_doi'):
                    continue
                doi = row[k]
                if doi not in status_of_doi:
                    response = requests.get(f'https://dx.doi.org/{doi}')
                    status_of_doi[doi] = response.status_code
                if status_of_doi[doi] != requests.codes.ok:
                    errors[f'{row_number}, {k} {doi}'] = status_of_doi[doi]

        return errors

    def _get_data_dir_errors(self, assay_type, data_path):
        return get_data_dir_errors(
            assay_type, data_path, dataset_ignore_globs=self.dataset_ignore_globs)

    def _get_contributors_errors(self, contributors_path):
        return get_contributors_errors(contributors_path, self.encoding)

    def _get_antibodies_errors(self, antibodies_path):
        return get_antibodies_errors(antibodies_path, self.encoding)

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
            | set(self._get_contributors_references().keys()) \
            | set(self._get_antibodies_references().keys())
        non_metadata_paths = {
            path.name for path in self.directory_path.iterdir()
            if not path.name.endswith(TSV_SUFFIX)
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

    def _get_antibodies_references(self):
        return self._get_references('antibodies_path')

    def _get_contributors_references(self):
        return self._get_references('contributors_path')

    def _get_references(self, col_name):
        references = defaultdict(list)
        for tsv_path in self.effective_tsv_paths.keys():
            for i, row in enumerate(dict_reader_wrapper(tsv_path, self.encoding)):
                if col_name in row:
                    reference = f'{tsv_path} (row {i+2})'
                    references[row[col_name]].append(reference)
        return references
