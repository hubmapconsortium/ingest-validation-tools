import argparse
import os
import re


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
