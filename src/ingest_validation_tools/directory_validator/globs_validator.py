from os import walk
from fnmatch import fnmatch

from ingest_validation_tools.directory_validator.errors import \
    DirectoryValidationErrors


def validate(path, paths_dict, dataset_ignore_globs=[]):
    '''
    Given a directory path, and a dict representing valid path globs,
    raise DirectoryValidationErrors if there are errors.
    '''
    required_globs, allowed_globs = _get_required_allowed(paths_dict)
    (dir_path, dir_names, file_names) = walk(path)
    errors = []
    for file_name in file_names:
        if any(fnmatch(file_name, glob) for glob in dataset_ignore_globs):
            continue
        if not any(fnmatch(file_name, glob) for glob in allowed_globs):
            errors.append(f'Not allowed: {file_name}')
    for glob in required_globs:
        if not any(fnmatch(file_name, glob) for file_name in file_names):
            errors.append(f'Required but not found: {glob}')
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
    >>> _get_required_optional(nested)
    (['a'], ['a', 'b/c'])

    '''
    flat = _flatten(nested)
    required = []
    allowed = []
    for k, v in flat.items():
        allowed.append(k)
        if v:
            required.append(k)
    return required, optional


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
