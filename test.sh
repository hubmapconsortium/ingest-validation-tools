#!/usr/bin/env bash
set -o errexit

red=`tput setaf 1`
green=`tput setaf 2`
reset=`tput sgr0`
start() { [[ -z $CI ]] || echo travis_fold':'start:$1; echo $green$1$reset; }
end() { [[ -z $CI ]] || echo travis_fold':'end:$1; }
die() { set +v; echo "$red$*$reset" 1>&2 ; exit 1; }


start flake8
flake8 --exclude ingest-validation-tests || die 'Try: autopep8 --in-place --aggressive -r .'
end flake8

start src-doctests
cd src
find . | grep '\.py$' | xargs python -m doctest
cd -
end src-doctests

for TEST in test-*; do
  start $TEST
  eval ./$TEST
  end $TEST
done

start changelog
if [ "$TRAVIS_BRANCH" != 'master' ]; then
  diff CHANGELOG.md <(curl -s https://raw.githubusercontent.com/hubmapconsortium/ingest-validation-tools/master/CHANGELOG.md) \
    && die 'Update CHANGELOG.md'
fi
end changelog
