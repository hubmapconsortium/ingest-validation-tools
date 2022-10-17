from datetime import datetime
from collections import defaultdict
from fnmatch import fnmatch
from collections import Counter
from pathlib import Path
import subprocess

from ingest_validation_tools.validation_utils import (
    get_tsv_errors,
    get_data_dir_errors,
    dict_reader_wrapper,
    get_context_of_decode_error,
    get_table_schema_version,
    get_directory_schema_versions
)

from ingest_validation_tools.plugin_validator import (
    run_plugin_validators_iter,
    ValidatorError as PluginValidatorError
)

from ingest_validation_tools.schema_loader import (
    PreflightError
)


TSV_SUFFIX = 'metadata.tsv'


class Upload:
    def __init__(self, directory_path=None, tsv_paths=[],
                 optional_fields=[], add_notes=True,
                 dataset_ignore_globs=[], upload_ignore_globs=[],
                 plugin_directory=None, encoding=None, offline=None,
                 ignore_deprecation=False, extra_parameters={}):
        self.directory_path = directory_path
        self.optional_fields = optional_fields
        self.dataset_ignore_globs = dataset_ignore_globs
        self.upload_ignore_globs = upload_ignore_globs
        self.plugin_directory = plugin_directory
        self.encoding = encoding
        self.offline = offline
        self.add_notes = add_notes
        self.ignore_deprecation = ignore_deprecation
        self.errors = {}
        self.effective_tsv_paths = {}
        self.extra_parameters = extra_parameters
        try:
            unsorted_effective_tsv_paths = {
                str(path): get_table_schema_version(path, self.encoding)
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

    #####################
    #
    # Two public methods:
    #
    #####################

    def get_info(self) -> dict:
        git_version = subprocess.check_output(
            'git rev-parse --short HEAD'.split(' '),
            encoding='ascii',
            stderr=subprocess.STDOUT
        ).strip()

        effective_tsvs = {
            Path(path).name: {
                'Schema': sv.schema_name,
                'Metadata schema version': sv.version,
                'Directory schema versions':
                    get_directory_schema_versions(path, encoding='ascii')
            }
            for path, sv in self.effective_tsv_paths.items()
        }

        return {
            'Time': datetime.now(),
            'Git version': git_version,
            'Directory': str(self.directory_path),
            'TSVs': effective_tsvs
        }

    def get_errors(self, **kwargs) -> dict:
        # This creates a deeply nested dict.
        # Keys are present only if there is actually an error to report.
        # plugin_kwargs are passed to the plugin validators.

        kwargs.update(self.extra_parameters)
        if self.errors:
            return self.errors

        errors = {}
        tsv_errors = self._get_tsv_errors()
        if tsv_errors:
            errors['Metadata TSV Errors'] = tsv_errors

        reference_errors = self._get_reference_errors()
        if reference_errors:
            errors['Reference Errors'] = reference_errors

        plugin_errors = self._get_plugin_errors(**kwargs)
        if plugin_errors:
            errors['Plugin Errors'] = plugin_errors

        # TODO: Remove; Now handled by get_info()
        if self.add_notes:
            git_version = subprocess.check_output(
                'git rev-parse --short HEAD'.split(' '),
                encoding='ascii',
                stderr=subprocess.STDOUT
            ).strip()
            errors['Notes'] = {
                'Time': datetime.now(),
                'Git version': git_version,
                'Directory': str(self.directory_path),
                'Effective TSVs': list(self.effective_tsv_paths.keys())
            }
        return errors

    ###################################
    #
    # Top-level private methods:
    #
    ###################################

    def _get_tsv_errors(self) -> dict:
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
                self.__get_assay_tsv_errors(schema_name, path)
            single_tsv_external_errors = \
                self.__get_assay_reference_errors(schema_name, path)

            single_tsv_errors = {}
            if single_tsv_internal_errors:
                single_tsv_errors['Internal'] = single_tsv_internal_errors
            if single_tsv_external_errors:
                single_tsv_errors['External'] = single_tsv_external_errors
            if single_tsv_errors:
                errors[f'{path} (as {schema_name})'] = single_tsv_errors
        return errors

    def _get_reference_errors(self) -> dict:
        errors = {}
        no_ref_errors = self.__get_no_ref_errors()
        try:
            multi_ref_errors = self.__get_multi_ref_errors()
        except UnicodeDecodeError as e:
            return get_context_of_decode_error(e)
        if no_ref_errors:
            errors['No References'] = no_ref_errors
        if multi_ref_errors:
            errors['Multiple References'] = multi_ref_errors
        return errors

    def _get_plugin_errors(self, **kwargs) -> dict:
        plugin_path = self.plugin_directory
        if not plugin_path:
            return None
        errors = defaultdict(list)
        for metadata_path in self.effective_tsv_paths.keys():
            try:
                for k, v in run_plugin_validators_iter(metadata_path,
                                                       plugin_path,
                                                       **kwargs):
                    errors[k].append(v)
            except PluginValidatorError as e:
                # We are ok with just returning a single error, rather than all.
                errors['Unexpected Plugin Error'] = str(e)
        return dict(errors)  # get rid of defaultdict

    ##############################
    #
    # Supporting private methods:
    #
    ##############################

    def __get_ref_errors(self, ref_type: str, path: Path, assay_type: str) -> dict:
        if ref_type == 'data':
            return get_data_dir_errors(
                assay_type, path, dataset_ignore_globs=self.dataset_ignore_globs)
        else:
            return get_tsv_errors(
                schema_name=ref_type, tsv_path=path,
                offline=self.offline, encoding=self.encoding,
                ignore_deprecation=self.ignore_deprecation)

    def __get_assay_tsv_errors(self, assay_type: str, path: Path) -> dict:
        return get_tsv_errors(
            schema_name=assay_type, tsv_path=path,
            offline=self.offline, encoding=self.encoding,
            optional_fields=self.optional_fields,
            ignore_deprecation=self.ignore_deprecation)

    def __get_assay_reference_errors(self, assay_type: str, path: Path) -> dict:
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
            for ref in ['data', 'contributors', 'antibodies']:
                field = f'{ref}_path'
                if not row.get(field):
                    continue
                path = self.directory_path / row[field]
                ref_errors = self.__get_ref_errors(ref, path, assay_type)
                if ref_errors:
                    errors[f'{row_number}, {ref} {path}'] = ref_errors

        return errors

    def __get_no_ref_errors(self) -> dict:
        if not self.directory_path:
            return {}
        referenced_data_paths = set(self.__get_data_references().keys()) \
            | set(self.__get_contributors_references().keys()) \
            | set(self.__get_antibodies_references().keys())
        non_metadata_paths = {
            path.name for path in self.directory_path.iterdir()
            if not path.name.endswith(TSV_SUFFIX)
            and not any([
                fnmatch(path.name, glob)
                for glob in self.upload_ignore_globs
            ])
        }
        unreferenced_paths = non_metadata_paths - referenced_data_paths
        unreferenced_dir_paths = [path for path in unreferenced_paths if Path(path).is_dir()]
        unreferenced_file_paths = [path for path in unreferenced_paths if not Path(path).is_dir()]
        errors = {}
        if unreferenced_dir_paths:
            errors['Directories'] = unreferenced_dir_paths
        if unreferenced_file_paths:
            errors['Files'] = unreferenced_file_paths
        return errors

    def __get_multi_ref_errors(self) -> dict:
        errors = {}
        data_references = self.__get_data_references()
        for path, references in data_references.items():
            if len(references) > 1:
                errors[path] = references
        return errors

    def __get_data_references(self) -> dict:
        return self.__get_references('data_path')

    def __get_antibodies_references(self) -> dict:
        return self.__get_references('antibodies_path')

    def __get_contributors_references(self) -> dict:
        return self.__get_references('contributors_path')

    def __get_references(self, col_name) -> dict:
        references = defaultdict(list)
        for tsv_path in self.effective_tsv_paths.keys():
            for i, row in enumerate(dict_reader_wrapper(tsv_path, self.encoding)):
                if col_name in row:
                    reference = f'{tsv_path} (row {i+2})'
                    references[row[col_name]].append(reference)
        return references
