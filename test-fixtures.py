#!/usr/bin/env python

from doctest import testfile, REPORT_NDIFF

from pathlib import Path
import sys
import logging
import re
from glob import glob

sys.path.append('src')
from validate_submission import _validate_submission_directory_messages  # noqa E402


def make_validator(path):
    def print_messages():
        messages = _validate_submission_directory_messages(str(path))
        cleaned = re.sub(r'\n(\s*\n)+', '\n.\n', '\n'.join(messages)).strip()
        print(cleaned or 'Validation passed!')
    return print_messages


def main():
    # TODO: argparse
    logging.basicConfig(level=logging.INFO)

    total_failure_count = 0
    total_test_count = 0

    for doctest in (glob('tests/fixtures/**/*.doctest', recursive=True)):
        logging.info(f'doctest {doctest}...')
        print_messages = make_validator(Path(doctest).parent / 'submission')

        (failure_count, test_count) = \
            testfile(
                doctest,
                globs={'print_messages': print_messages},
                optionflags=REPORT_NDIFF)

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
