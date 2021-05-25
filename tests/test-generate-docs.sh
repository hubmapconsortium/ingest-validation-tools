#!/usr/bin/env bash
set -o errexit

red=`tput setaf 1`
reset=`tput sgr0`
die() { set +v; echo "$red$*$reset" 1>&2 ; exit 1; }

# Test field-descriptions.yaml:

REAL_DEST="docs/field-descriptions.yaml"
TEST_DEST="docs-test/field-descriptions.yaml"

REAL_CMD="src/generate_field_descriptions.py > $REAL_DEST"
TEST_CMD="src/generate_field_descriptions.py > $TEST_DEST"

mkdir docs-test || echo "Already exists"
eval $TEST_CMD || die "Command failed: $TEST_CMD"
diff -r $REAL_DEST $TEST_DEST \
  || die "Update needed: $REAL_CMD; $LOOP"
rm -rf docs-test

# Test docs:

for TYPE in $(ls -d docs/*); do
  # Skip directories that are unpopulated:
  TYPE=`basename $TYPE`
  [ -e docs/$TYPE/$TYPE-metadata.tsv ] || continue

  echo "Testing $TYPE generation..."

  REAL_DEST="docs/$TYPE"
  TEST_DEST="docs-test/$TYPE"

  REAL_CMD="src/generate_docs.py $TYPE $REAL_DEST"
  TEST_CMD="src/generate_docs.py $TYPE $TEST_DEST"

  mkdir -p $TEST_DEST || echo "$TEST_DEST already exists"
  eval $TEST_CMD
  diff -r $REAL_DEST $TEST_DEST \
    || die "Update needed: $REAL_CMD
Or:" 'for D in `ls -d docs/*/`; do D=`basename D`; [ -e docs/$D/$D-metadata.tsv ] || continue; src/generate_docs.py `basename $D` $D; done'
  rm -rf $TEST_DEST
  ((++GENERATE_COUNT))
done
[[ $GENERATE_COUNT -gt 0 ]] || die "No files generated"
