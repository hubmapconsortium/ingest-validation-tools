#!/usr/bin/env bash
set -o errexit

red=`tput setaf 1`
green=`tput setaf 2`
reset=`tput sgr0`
start() { [[ -z $CI ]] || echo travis_fold':'start:$1; echo $green$1$reset; }
end() { [[ -z $CI ]] || echo travis_fold':'end:$1; }
die() { set +v; echo "$red$*$reset" 1>&2 ; exit 1; }

start flake8
flake8 || die 'Try: autopep8 --in-place --aggressive -r .'
end flake8

# start pytest
# pytest -vv
# end pytest

start fixtures
for TYPE in $(ls src/hubmap_ingest_validator/directory-schemas/datasets); do
  TYPE=$(echo $TYPE | sed -e 's/.yaml//')
  src/validate.py --logging INFO tests/fixtures/$TYPE $TYPE
  ((++FIXTURES_COUNT))
done
[[ $FIXTURES_COUNT -gt 0 ]] || die "No fixtures tested"
end fixtures

start doctests
cd src
python -m doctest -v README.md
cd -
end doctests

start generate
for TYPE in $(ls docs); do
  for TARGET_EXT in template.tsv schema.yaml; do
    echo "Testing $TYPE $TARGET_EXT generation..."
    TARGET=${TARGET_EXT%.*}
    CMD="src/generate.py $TYPE $TARGET"
    DEST="docs/$TYPE/$TARGET_EXT"
    diff "$DEST" <($CMD) \
      || die "Update needed: $CMD > $DEST"
  done
  ((++GENERATE_COUNT))
done
[[ $GENERATE_COUNT -gt 0 ]] || die "No files generated"
end generate

start changelog
if [ "$TRAVIS_BRANCH" != 'master' ]; then
  diff CHANGELOG.md <(curl -s https://raw.githubusercontent.com/hubmapconsortium/ingest-validation-tools/master/CHANGELOG.md) \
    && die 'Update CHANGELOG.md'
fi
end changelog
