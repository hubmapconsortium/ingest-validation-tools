from os import walk
from fnmatch import fnmatch


class DirectoryValidationErrors(Exception):
    def __init__(self, errors):
        self.errors = errors

    def __str__(self):
        return '\n'.join(self.errors)


def validate(path, paths_dict, dataset_ignore_globs=[]):
    '''
    Given a directory path, and a dict representing valid path globs,
    raise DirectoryValidationErrors if there are errors.
    '''
    required_globs, allowed_globs = _get_required_allowed(paths_dict)
    errors = []
    for triple in walk(path):
        (dir_path, dir_names, file_names) = triple
        prefix = dir_path.replace(str(path), '')
        actual_paths = (
            [f'{prefix}/{name}' for name in file_names]
            if prefix else file_names
        )
        for actual in actual_paths:
            if any(fnmatch(actual, glob) for glob in dataset_ignore_globs):
                continue
            if not any(fnmatch(actual, glob) for glob in allowed_globs):
                errors.append(f'Not allowed: {actual}')
        for glob in required_globs:
            if not any(fnmatch(actual, glob) for actual in actual_paths):
                errors.append(f'Required but not found: {glob}')
        print(errors)
        if errors:
            raise DirectoryValidationErrors(errors)


def _get_required_allowed(nested):
    '''
    Given a nested dict, flatten it and separate the keys with
    falsy values from those with truthy values.

    >>> nested = {
    ...   'a': 1,
    ...   'b': {'c': 0}
    ... }
    >>> _get_required_allowed(nested)
    (['a'], ['a', 'b/c'])

    '''
    flat = _flatten(nested)
    required = []
    allowed = []
    for k, v in flat.items():
        allowed.append(k)
        if v:
            required.append(k)
    return required, allowed


def _flatten(nested, joiner='/'):
    '''
    Given a nested dict, flatten it to a single layer dict,
    with keys constructed by chaining the keys of the original.

    >>> nested = {
    ...   'x.txt': 1,
    ...   'a': {
    ...     'y.txt': 0,
    ...     'b': {
    ...       'c': {},
    ...       'd': {
    ...         'z.txt': 1 }}}}
    >>> _flatten(nested)
    {'x.txt': 1, 'a/y.txt': 0, 'a/b/d/z.txt': 1}

    '''
    flat = {}
    for key, value in nested.items():
        if type(value) != dict:
            flat[key] = value
        else:
            for k, v in _flatten(value).items():
                flat[f'{key}{joiner}{k}'] = v
    return flat
