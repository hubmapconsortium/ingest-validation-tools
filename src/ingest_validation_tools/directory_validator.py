import os
import re
from fnmatch import fnmatch


class DirectoryValidationErrors(Exception):
    def __init__(self, errors):
        self.errors = errors


def validate_directory(path, paths_dict, dataset_ignore_globs=[]):
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
    for triple in os.walk(path):
        (dir_path, _dir_names, file_names) = triple
        # [1:] removes leading '/', if any.
        prefix = dir_path.replace(str(path), '')[1:]
        if os.name == 'nt':
            # Convert MS backslashes to forward slashes.
            prefix = prefix.replace('\\', '/')
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
        errors['Not allowed'] = sorted(not_allowed_errors)
    if required_missing_errors:
        errors['Required but missing'] = sorted(required_missing_errors)
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
