#!/usr/bin/env bash
set -o errexit

red=`tput setaf 1`
reset=`tput sgr0`
die() { set +v; echo "$red$*$reset" 1>&2 ; exit 1; }

REAL_DEST="docs/sample"
TEST_DEST="docs-test/sample"

REAL_CMD="src/generate_other_docs.py $REAL_DEST"
TEST_CMD="src/generate_other_docs.py $TEST_DEST"

mkdir -p docs-test/sample || echo "Already exists"
eval $TEST_CMD
diff -r $REAL_DEST $TEST_DEST \
  || die "Update needed: $REAL_CMD"
rm -rf docs-test