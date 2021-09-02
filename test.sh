#!/usr/bin/env bash
set -o errexit

echo 'start?'

if [[ ! -z "$TERM" ]]; then
  red=`tput setaf 1`
  green=`tput setaf 2`
  reset=`tput sgr0`
fi

echo 'call tput?'

start() { [[ -z $CI ]] || echo travis_fold':'start:$1; echo $green$1$reset; }
end() { [[ -z $CI ]] || echo travis_fold':'end:$1; }
die() { set +v; echo "$red$*$reset" 1>&2 ; exit 1; }

echo 'functions?'

CONTINUE_FROM="$1"

if [[ -z $CONTINUE_FROM ]]; then
  start flake8
  flake8 src || die 'Try: autopep8 --in-place --aggressive -r .'
  end flake8

  start mypy
  mypy
  end mypy
fi

for TEST in tests/test-*; do
  if [[ -z $CONTINUE_FROM ]] || [[ $CONTINUE_FROM = $TEST ]]; then
    CONTINUE_FROM=''
    start $TEST
    eval $TEST
    end $TEST
  fi
done

start changelog
if [ "$TRAVIS_BRANCH" != 'main' ]; then
  diff CHANGELOG.md <(curl -s https://raw.githubusercontent.com/hubmapconsortium/ingest-validation-tools/main/CHANGELOG.md) \
    && die 'Update CHANGELOG.md'
fi
end changelog
