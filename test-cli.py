#!/usr/bin/env python

import subprocess


def validate(args):
    cmd = ['src/validate_submission.py'] + args.split(' ')
    subprocess.run(
        cmd, check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL)


good_args = [
    '--help',
    '--type_metadata '
    'atacseq:tests/fixtures/good-atacseq/submission/atacseq-metadata.tsv',
    '--local_directory tests/fixtures/good-atacseq/submission/'
]

for args in good_args:
    validate(args)


bad_args = [
    '',
    '--bad',
    '--type_metadata '
    'codex:tests/fixtures/good-atacseq/submission/atacseq-metadata.tsv',
    '--local_directory tests/fixtures/bad-mixed/submission/'
]

for args in bad_args:
    try:
        validate(args)
    except subprocess.CalledProcessError:
        # Expected!
        continue
    raise Exception(f'Passed, when it should have failed: {args}')
