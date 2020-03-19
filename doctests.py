#!/usr/bin/env python

from doctest import testfile
from pathlib import Path
import sys

sys.path.append('src')
import validate # noqa E402


def main():
    doctests = [
        str(p) for p in
        (Path('tests') / 'fixtures').iterdir()
        if p.suffix == '.doctest'
    ]

    total_failure_count = 0
    total_test_count = 0

    for doctest in doctests:
        (failure_count, test_count) = \
            testfile(doctest, globs={'validate': validate}, verbose=True)
        total_failure_count += failure_count
        total_test_count += test_count

    if total_failure_count > 0:
        print('Doctest failures')
        return 1
    if total_test_count == 0:
        print('No doctests run')
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
