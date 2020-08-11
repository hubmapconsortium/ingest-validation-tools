from os import walk
from fnmatch import fnmatch


class DirectoryValidationErrors(Exception):
    def __init__(self, errors):
        self.errors = errors


def validate_directory(path, paths_dict, dataset_ignore_globs=[]):
    '''
    Given a directory path, and a dict representing valid path globs,
    raise DirectoryValidationErrors if there are errors.
    '''
    required_globs, allowed_globs = _get_required_allowed(paths_dict)
    required_missing_errors, not_allowed_errors = ([], [])
    if not path.exists():
        raise DirectoryValidationErrors({
            'No such file or directory': str(path)
        })
    actual_paths = []
    for triple in walk(path):
        (dir_path, dir_names, file_names) = triple
        # [1:] removes leading '/', if any.
        prefix = dir_path.replace(str(path), '')[1:]
        actual_paths += (
            [f'{prefix}/{name}' for name in file_names]
            if prefix else file_names
        )

    for actual in actual_paths:
        if any(fnmatch(actual, glob) for glob in dataset_ignore_globs):
            continue
        if not any(fnmatch(actual, glob) for glob in allowed_globs):
            not_allowed_errors.append(actual)
    for glob in required_globs:
        if not any(fnmatch(actual, glob) for actual in actual_paths):
            required_missing_errors.append(glob)

    errors = {}
    if not_allowed_errors:
        errors['Not allowed'] = not_allowed_errors
    if required_missing_errors:
        errors['Required but missing'] = required_missing_errors
    if errors:
        raise DirectoryValidationErrors(errors)


def _get_required_allowed(nested):
    '''
    Given a nested dict, flatten it and separate the keys
    which are required from those that are allowed.

    >>> nested = {
    ...   'a': {'description': 'A'},
    ...   'b': {'c': {'required': False, 'description': 'C'}}
    ... }
    >>> _get_required_allowed(nested)
    (['a'], ['a', 'b/c'])

    '''
    flat = _flatten(nested)
    required = []
    allowed = []
    for k, v in flat.items():
        allowed.append(k)
        if 'required' not in v or v['required']:
            required.append(k)
    return required, allowed


def _flatten(nested, joiner='/'):
    '''
    Given a nested dict, flatten it to a two layer dict,
    with keys constructed by chaining the keys of the original.

    >>> nested = {
    ...   'x.txt': {'description': 'X'},
    ...   'a': {
    ...     'y.txt': {'required': False, 'description': 'Y'},
    ...     'b': {
    ...       'c': {},
    ...       'd': {
    ...         'z.txt': {'description': 'Z'} }}}}
    >>> from pprint import pprint
    >>> pprint(_flatten(nested))
    {'a/b/d/z.txt': {'description': 'Z'},
     'a/y.txt': {'description': 'Y', 'required': False},
     'x.txt': {'description': 'X'}}

    '''
    flat = {}
    for key, value in nested.items():
        if 'description' in value:
            flat[key] = value
        else:
            for k, v in _flatten(value).items():
                flat[f'{key}{joiner}{k}'] = v
    return flat
