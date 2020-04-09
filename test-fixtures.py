#!/usr/bin/env python

from doctest import testfile, REPORT_NDIFF

from pathlib import Path
import sys
import logging
import re

sys.path.append('src')
import validate_submission  # noqa E402


def print_messages(submission_directory):
    messages = validate_submission._validate_submission_directory_messages(
        submission_directory)
    cleaned = re.sub(r'\n(\s*\n)+', '\n.\n', '\n'.join(messages)).strip()
    print(cleaned or 'Validation passed!')


def main():
    # TODO: argparse
    logging.basicConfig(level=logging.INFO)

    doctests = [
        str(p) for p in
        (Path('tests') / 'fixtures').iterdir()
        if p.suffix == '.doctest'
    ]

    total_failure_count = 0
    total_test_count = 0

    for doctest in doctests:
        logging.info(f'doctest {doctest}...')
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
