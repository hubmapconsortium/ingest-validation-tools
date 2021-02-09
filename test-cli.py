#!/usr/bin/env python

import subprocess

# NOTE: Starting subprocesses is slow, so these lists should be kept short.
# Fixtures or doctests should be used for the details:
# They run faster, and tell us more when there is a failure.
good_args = [
    '--local_directory dataset-examples/good-scatacseq/submission/ '
    '--dataset_ignore_globs ignore-*.tsv .* '
    '--submission_ignore_globs drv_ignore_*'
    # NOTE: When called from the shell,
    # remember to quote '*' arguments to prevent expansion.
]
bad_args = [
    '--bad',
]


def validate(args):
    cmd = [
        'src/validate_submission.py', '--output', 'as_text'
    ] + args.split(' ')
    subprocess.run(
        cmd, check=True)


for args in good_args:
    validate(args)
for args in bad_args:
    try:
        validate(args)
    except subprocess.CalledProcessError:
        print('☝️  That was an expected error.')
        continue
    raise Exception(f'Passed, when it should have failed: {args}')
