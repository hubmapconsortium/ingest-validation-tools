#!/usr/bin/env bash
set -o errexit

die() { set +v; echo "$*" 1>&2 ; exit 1; }

echo "Checking typing with mypy..."
mypy --config-file=pyproject.toml
echo "Running doctests with pytest..."
pytest --doctest-modules --ignore="tests/" --ignore="_deprecated/"

BRANCH="$(git rev-parse --abbrev-ref HEAD)"

if [[ "$BRANCH" == 'main' ]] ; then
    echo "On GitHub branch $BRANCH, not checking CHANGELOG.md"
elif [[ ! $(git symbolic-ref --short HEAD) ]] ; then
    echo "Not on branch, not checking CHANGELOG.md (should only happen on tagged release)"
else
    echo "GitHub branch: $BRANCH"
    echo "Checking CHANGELOG.md..."
    diff CHANGELOG.md <(curl -s https://raw.githubusercontent.com/hubmapconsortium/ingest-validation-tools/main/CHANGELOG.md) \
        && die 'Update CHANGELOG.md'
fi

# In this case, a successful diff would exit non-zero, so we need an explicit exit.
exit 0
