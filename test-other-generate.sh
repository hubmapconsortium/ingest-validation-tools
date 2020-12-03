#!/usr/bin/env bash
set -o errexit

red=`tput setaf 1`
reset=`tput sgr0`
die() { set +v; echo "$red$*$reset" 1>&2 ; exit 1; }

for TARGET in 'sample' 'contributors' 'antibodies'; do
  REAL_DEST="docs/$TARGET"
  TEST_DEST="docs-test/$TARGET"

  REAL_CMD="src/generate_docs.py $TARGET $REAL_DEST"
  TEST_CMD="src/generate_docs.py $TARGET $TEST_DEST"

  mkdir -p $TEST_DEST || echo "Already exists"
  echo "Running: $TEST_CMD"
  eval $TEST_CMD
  diff -r $REAL_DEST $TEST_DEST --exclude='*.xlsx' \
    || die "Update needed: $REAL_CMD"
  rm -rf docs-test
done