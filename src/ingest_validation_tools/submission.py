from datetime import datetime
from collections import defaultdict
from fnmatch import fnmatch
from pathlib import Path
from collections import Counter

from ingest_validation_tools.yaml_include_loader import load_yaml

from ingest_validation_tools.validation_utils import (
    get_tsv_errors,
    get_data_dir_errors,
    dict_reader_wrapper,
    get_context_of_decode_error
)

from ingest_validation_tools.plugin_validator import (
    run_plugin_validators_iter,
    ValidatorError as PluginValidatorError
)

from ingest_validation_tools.schema_loader import (
    SchemaVersion
)


def _assay_to_schema_name(name):
    '''
    Given an assay name, read all the schemas until one matches.
    Return the schema name, but not the version.
    '''
    for path in (Path(__file__).parent / 'table-schemas' / 'assays').glob('*.yaml'):
        schema = load_yaml(path)
        for field in schema['fields']:
            if field['name'] == 'assay_type' and name in field['constraints']['enum']:
                return path.stem.split('-v')[0]
    raise PreflightError(f"Can't find schema where '{name}' is in the enum for assay_type")


TSV_SUFFIX = 'metadata.tsv'


class PreflightError(Exception):
    pass


class Submission:
    def __init__(self, directory_path=None, tsv_paths=[],
                 optional_fields=[], add_notes=True,
                 dataset_ignore_globs=[], submission_ignore_globs=[],
                 plugin_directory=None, encoding=None, offline=None):
        self.directory_path = directory_path
        self.optional_fields = optional_fields
        self.dataset_ignore_globs = dataset_ignore_globs
        self.submission_ignore_globs = submission_ignore_globs
        self.plugin_directory = plugin_directory
        self.encoding = encoding
        self.offline = offline
        self.add_notes = add_notes
        self.errors = {}
        try:
            unsorted_effective_tsv_paths = {
                str(path): self._get_schema_version(path)
                for path in (
                    tsv_paths if tsv_paths
                    else directory_path.glob(f'*{TSV_SUFFIX}')
                )
            }
            self.effective_tsv_paths = {
                k: unsorted_effective_tsv_paths[k]
                for k in sorted(unsorted_effective_tsv_paths.keys())
            }
        except PreflightError as e:
            self.errors['Preflight'] = str(e)

    def _get_schema_version(self, path):
        try:
            rows = dict_reader_wrapper(path, self.encoding)
        except UnicodeDecodeError:
            return None
            # TODO: use get_context_of_decode_error
        except IsADirectoryError:
            raise PreflightError(f'Expected a TSV, found a directory at {path}.')
        if not rows:
            raise PreflightError(f'{path} has no data rows.')
        if 'assay_type' not in rows[0]:
            message = f'{path} does not contain "assay_type". '
            if 'channel_id' in rows[0]:
                message += 'Has "channel_id": Antibodies TSV found where metadata TSV expected.'
            elif 'orcid_id' in rows[0]:
                message += 'Has "orcid_id": Contributors TSV found where metadata TSV expected.'
            else:
                message += f'Column headers: {", ".join(rows[0].keys())}'
            raise PreflightError(message)

        assay = rows[0]['assay_type']
        version = rows[0]['version'] if 'version' in rows[0] else 0
        schema_name = _assay_to_schema_name(assay)
        if 'source_project' in rows[0]:
            schema_name += f"-{rows[0]['source_project']}"

        return SchemaVersion(schema_name, version)

    def get_errors(self):
        # This creates a deeply nested dict.
        # Keys are present only if there is actually an error to report.
        if self.errors:
            return self.errors

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
                'Effective TSVs': list(self.effective_tsv_paths.keys())
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

        types_counter = Counter([v.schema_name for v in self.effective_tsv_paths.values()])
        repeated = [
            assay_type
            for assay_type, count in types_counter.items()
            if count > 1
        ]
        if repeated:
            return f'There is more than one TSV for this type: {", ".join(repeated)}'

        errors = {}
        for path, schema_version in self.effective_tsv_paths.items():
            schema_name = schema_version.schema_name

            single_tsv_internal_errors = \
                self._get_assay_internal_errors(schema_name, path)
            single_tsv_external_errors = \
                self._get_assay_reference_errors(schema_name, path)

            single_tsv_errors = {}
            if single_tsv_internal_errors:
                single_tsv_errors['Internal'] = single_tsv_internal_errors
            if single_tsv_external_errors:
                single_tsv_errors['External'] = single_tsv_external_errors
            if single_tsv_errors:
                errors[f'{path} (as {schema_name})'] = single_tsv_errors
        return errors

    def _get_data_dir_errors(self, assay_type, data_path):
        return get_data_dir_errors(
            assay_type, data_path, dataset_ignore_globs=self.dataset_ignore_globs)

    def _get_contributors_errors(self, contributors_path):
        return get_tsv_errors(
            schema_name='contributors', tsv_path=contributors_path,
            offline=self.offline, encoding=self.encoding)

    def _get_antibodies_errors(self, antibodies_path):
        return get_tsv_errors(
            schema_name='antibodies', tsv_path=antibodies_path,
            offline=self.offline, encoding=self.encoding)

    def _get_assay_internal_errors(self, assay_type, path):
        return get_tsv_errors(
            schema_name=assay_type, tsv_path=path,
            offline=self.offline, encoding=self.encoding,
            optional_fields=self.optional_fields)

    def _get_assay_reference_errors(self, assay_type, path):
        try:
            rows = dict_reader_wrapper(path, self.encoding)
        except UnicodeDecodeError as e:
            return get_context_of_decode_error(e)
        except IsADirectoryError:
            return f'Expected a TSV, found a directory at {path}.'
        if 'data_path' not in rows[0] or 'contributors_path' not in rows[0]:
            return 'File is missing data_path or contributors_path.'
        if not self.directory_path:
            return None

        errors = {}
        for i, row in enumerate(rows):
            row_number = f'row {i+2}'

            data_path = self.directory_path / \
                row['data_path']
            data_dir_errors = self._get_data_dir_errors(
                assay_type, data_path)
            if data_dir_errors:
                errors[f'{row_number}, referencing {data_path}'] = data_dir_errors

            contributors_path = self.directory_path / row['contributors_path']
            contributors_errors = self._get_contributors_errors(contributors_path)
            if contributors_errors:
                errors[f'{row_number}, contributors {contributors_path}'] = \
                    contributors_errors

            if 'antibodies_path' in row:
                antibodies_path = self.directory_path / row['antibodies_path']
                antibodies_errors = self._get_antibodies_errors(antibodies_path)
                if antibodies_errors:
                    errors[f'{row_number}, antibodies {antibodies_path}'] = \
                        antibodies_errors

        return errors

    def _get_reference_errors(self):
        errors = {}
        no_ref_errors = self._get_no_ref_errors()
        try:
            multi_ref_errors = self._get_multi_ref_errors()
        except UnicodeDecodeError as e:
            return get_context_of_decode_error(e)
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
