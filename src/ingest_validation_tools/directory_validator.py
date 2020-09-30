from os import walk
import re
from fnmatch import fnmatch
from importlib import import_module

DIRECTORY_CONTENT_VALIDATOR_FACTORY = default_factory


class DirectoryContentValidator(object):
    def __init__(self, base_path, assay_type):
        self.base_path = base_path
        self.assay_type = assay_type

    def collect_errors(self):
        """
        returns string or None.  Multiple errors are to be reported
        via a single multi-line string.
        """
        return None


class DefaultDirectoryContentValidator(DirectoryContentValidator):
    """
    Implements backward compatible calls to content validation modules
    """
    def collect_errors(self):
        validator = import_module(
            f'ingest_validation_tools.content_validation.{self.assay_type}')
        return validator.collect_errors(self.base_path)


def default_factory(base_path, assay_type):
    """
    default validator factory
    """
    return DefaultDirectoryContentValidator(base_path, assay_type)


class DirectoryValidationErrors(Exception):
    def __init__(self, errors):
        self.errors = errors


def validate_directory_structure(path, paths_dict, dataset_ignore_globs=[]):
    '''
    Given a directory path, and a dict representing valid path globs,
    raise DirectoryValidationErrors if there are errors.
    '''
    required_patterns, allowed_patterns = _get_required_allowed(paths_dict)
    required_missing_errors, not_allowed_errors = ([], [])
    if not path.exists():
        raise DirectoryValidationErrors({
            'No such file or directory': str(path)
        })
    actual_paths = []
    for triple in walk(path):
        (dir_path, _dir_names, file_names) = triple
        # [1:] removes leading '/', if any.
        prefix = dir_path.replace(str(path), '')[1:]
        actual_paths += (
            [f'{prefix}/{name}' for name in file_names]
            if prefix else file_names
        )

    for actual in actual_paths:
        if any(fnmatch(actual, glob) for glob in dataset_ignore_globs):
            continue
        if not any(
                re.fullmatch(pattern, actual)
                for pattern in allowed_patterns):
            not_allowed_errors.append(actual)
    for pattern in required_patterns:
        if not any(re.fullmatch(pattern, actual) for actual in actual_paths):
            required_missing_errors.append(pattern)

    errors = {}
    if not_allowed_errors:
        errors['Not allowed'] = not_allowed_errors
    if required_missing_errors:
        errors['Required but missing'] = required_missing_errors
    if errors:
        raise DirectoryValidationErrors(errors)


def _get_required_allowed(dir_schema):
    '''
    Given a directory_schema, return a pair of regex lists:
    Those regexes which are required, and those which are allowed.

    >>> schema = [
    ...    {'pattern': 'this_is_required'},
    ...    {'pattern': 'this_is_optional', 'required': False}
    ... ]
    >>> _get_required_allowed(schema)
    (['this_is_required'], ['this_is_required', 'this_is_optional'])

    '''
    allowed = [
        item['pattern'] for item in dir_schema]
    required = [
        item['pattern'] for item in dir_schema
        if 'required' not in item or item['required']]
    return required, allowed


def validate_directory_content(assay_type, data_path):
    validator = DIRECTORY_CONTENT_VALIDATOR_FACTORY(data_path, assay_type)
    errors = validator.collect_errors()
    if errors:
        raise DirectoryValidationErrors(errors)
