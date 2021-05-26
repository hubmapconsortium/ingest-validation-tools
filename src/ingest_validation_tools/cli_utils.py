import os
from collections import namedtuple


class ShowUsageException(Exception):
    pass


def dir_path(s):
    if os.path.isdir(s):
        return s
    else:
        raise ShowUsageException(f'"{s}" is not a directory')


exit_codes = namedtuple(
    'ExitCode',
    ['VALID', 'BUG', 'ERROR', 'INVALID']
)(0, 1, 2, 3)
