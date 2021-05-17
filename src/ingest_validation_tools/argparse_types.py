import os


class ShowUsageException(Exception):
    pass


def dir_path(s):
    if os.path.isdir(s):
        return s
    else:
        raise ShowUsageException(f'"{s}" is not a directory')
