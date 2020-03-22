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

start src-doctests
find src | grep '\.py$' | xargs python -m doctest
end src-doctests

# start pytest
# pytest -vv
# end pytest

start fixtures
echo 'NOTE: There will be warnings below, generated from fixtures which should cause warnings!'
./test-fixtures.py
end fixtures

start generate
for TYPE in $(ls docs | grep -v README.md); do # Ignore README and just get subdirectories
  for TARGET in template.tsv schema.yaml README.md; do
    echo "Testing $TYPE $TARGET generation..."
    CMD="src/generate.py $TYPE $TARGET"
    DEST="docs/$TYPE/$TARGET"
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
