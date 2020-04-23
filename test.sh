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

start examples
./test-examples.sh
end examples

start generate
./test-generate.sh
end generate

start cli-docs
for TOOL in validate_submission.py generate_docs.py; do
  echo "Testing $TOOL docs..."
  [ -e src/$TOOL ] || die "src/$TOOL does not exist."
  diff \
        <(perl -ne 'print if /usage: '$TOOL'/../```/ and ! /```/' README.md) \
        <(src/$TOOL -h) \
      || die "Update README.md: src/$TOOL -h"
done
end cli-docs

start test-cli
./test-cli.py
end test-cli

start changelog
if [ "$TRAVIS_BRANCH" != 'master' ]; then
  diff CHANGELOG.md <(curl -s https://raw.githubusercontent.com/hubmapconsortium/ingest-validation-tools/master/CHANGELOG.md) \
    && die 'Update CHANGELOG.md'
fi
end changelog
