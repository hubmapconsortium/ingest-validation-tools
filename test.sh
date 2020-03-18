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
for TYPE in $(ls src/hubmap_ingest_validator/directory-schemas/datasets); do
  TYPE=$(echo $TYPE | sed -e 's/.yaml//')
  echo "Testing '$TYPE' fixture..."
  src/validate.py tests/fixtures/$TYPE $TYPE
done
end fixtures

start doctests
cd src
python -m doctest -v README.md
cd -
end doctests

start generate
for TYPE in $(ls docs); do
  TYPE=$(echo $TYPE | sed -e 's/.tsv//')
  echo "Testing '$TYPE' template generation..."
  diff docs/$TYPE.tsv <(src/generate.py $TYPE) \
    || die "Update docs/$TYPE.tsv"
done
end generate

start changelog
if [ "$TRAVIS_BRANCH" != 'master' ]; then
  diff CHANGELOG.md <(curl -s https://raw.githubusercontent.com/hubmapconsortium/ingest-validation-tools/master/CHANGELOG.md) \
    && die 'Update CHANGELOG.md'
fi
end changelog
