#!/usr/bin/env python

import subprocess

# NOTE: Starting subprocesses is slow, so these lists should be kept short.
# Fixtures or doctests should be used for the details:
# They run faster, and tell us more when there is a failure.
good_args = [
    '--local_directory examples/good-atacseq/submission/ '
    '--dataset_ignore_globs ignore-me.tsv',

    '--type_metadata atacseq '
    'examples/good-atacseq/submission/atacseq-metadata.tsv'
]
bad_args = [
    '--bad',
]


def validate(args):
    cmd = ['src/validate_submission.py'] + args.split(' ')
    subprocess.run(
        cmd, check=True)


for args in good_args:
    validate(args)
for args in bad_args:
    try:
        validate(args)
    except subprocess.CalledProcessError:
        # Expected!
        continue
    raise Exception(f'Passed, when it should have failed: {args}')
