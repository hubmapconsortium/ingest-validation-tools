import argparse
import os
import re
from urllib.parse import urlparse, parse_qs


class ShowUsageException(Exception):
    pass


def dir_path(s):
    if os.path.isdir(s):
        return s
    else:
        raise ShowUsageException(f'"{s}" is not a directory')


def origin_directory_pair(s):
    try:
        origin, path = s.split(':')
    except ValueError:
        raise argparse.ArgumentTypeError(
            f'Expected colon-delimited pair, not "{s}"')

    expected_format = r'[0-9a-f-]{36}'
    if not re.match(expected_format, origin):
        raise argparse.ArgumentTypeError(
            f'Origin format wrong; expected {expected_format}')

    return {
        'origin': origin,
        'path': path
    }


def globus_url(s):
    '''
    >>> globus_url('http://example.com/')
    Traceback (most recent call last):
    ...
    argparse.ArgumentTypeError: Expected a URL starting with https://app.globus.org/file-manager?

    >>> globus_url('https://app.globus.org/file-manager?a=1')
    Traceback (most recent call last):
    ...
    argparse.ArgumentTypeError: Expected query keys to be ['origin_id', 'origin_path'], not ['a']

    >>> globus_url('https://app.globus.org/file-manager?origin_id=32-hex-digits&origin_path=%2Fpath%2F')
    {'origin': '32-hex-digits', 'path': '/path/'}

    '''  # noqa E501
    expected_base = 'https://app.globus.org/file-manager?'
    if not s.startswith(expected_base):
        raise argparse.ArgumentTypeError(
            f'Expected a URL starting with {expected_base}')

    parsed = urlparse(s)
    query = parse_qs(parsed.query)
    expected_keys = ['origin_id', 'origin_path']
    actual_keys = sorted(query.keys())
    if actual_keys != expected_keys:
        raise argparse.ArgumentTypeError(
            f'Expected query keys to be {expected_keys}, not {actual_keys}')

    return {
        'origin': query['origin_id'][0],
        'path': query['origin_path'][0]
    }
