#!/usr/bin/env python

from doctest import testfile
from pathlib import Path
import sys

sys.path.append('src')
import validate


def main():
    doctests = [
        str(p) for p in
        (Path('tests') / 'fixtures').iterdir()
        if p.suffix == '.doctest'
    ]
    for doctest in doctests:
        testfile(doctest)
    # (failure_count, test_count)
    return 0


if __name__ == "__main__":
    sys.exit(main())
