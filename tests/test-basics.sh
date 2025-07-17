#!/usr/bin/env bash
set -o errexit

die() { set +v; echo "$*" 1>&2 ; exit 1; }

flake8 src || die 'Try: autopep8 --in-place --aggressive -r .'
mypy
pytest --doctest-modules --ignore-glob="tests-manual/" "tests/test_dataset_examples.py"

BRANCH="$(git rev-parse --abbrev-ref HEAD)"
echo "GitHub branch: $BRANCH"
if [ "$BRANCH" != 'main' ]; then
    echo "Checking CHANGELOG.md..."
    diff CHANGELOG.md <(curl -s https://raw.githubusercontent.com/hubmapconsortium/ingest-validation-tools/main/CHANGELOG.md) \
        && die 'Update CHANGELOG.md'
fi

# In this case, a successful diff would exit non-zero, so we need an explicit exit.
exit 0
