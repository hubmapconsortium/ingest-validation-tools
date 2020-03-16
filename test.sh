#!/usr/bin/env bash
set -o errexit

start() { echo travis_fold':'start:$1; echo $1; }
end() { echo travis_fold':'end:$1; }
die() { set +v; echo "$*" 1>&2 ; sleep 1; exit 1; }

start flake8
flake8 || die 'Try "autopep8 --in-place --aggressive -r ."'
end flake8

# start pytest
# pytest -vv
# end pytest

start fixtures
for FIXTURE in $(ls tests/fixtures); do
  src/hubmap_ingest_validator/cli.py tests/fixtures/$FIXTURE $FIXTURE
done
end fixtures

# start changelog
# if [ "$TRAVIS_BRANCH" != 'master' ]; then
#   diff CHANGELOG.md <(curl https://raw.githubusercontent.com/hubmapconsortium/ingest-validation-tools/master/CHANGELOG.md) \
#     && die 'Update CHANGELOG.md'
# fi
# end changelog
