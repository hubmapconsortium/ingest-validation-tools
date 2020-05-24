def _get_required_optional(nested):
    '''
    Given a nested dict, flatten it and separate the keys with
    falsy values from those with truthy values.

    >>> nested = {
    ...   'a': 1,
    ...   'b': {'c': 0}
    ... }
    >>> _get_required_optional(nested)
    (['a'], ['b/c'])

    '''
    flat = _flatten(nested)
    required = []
    optional = []
    for k, v in flat.items():
        if v:
            required.append(k)
        else:
            optional.append(k)
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
