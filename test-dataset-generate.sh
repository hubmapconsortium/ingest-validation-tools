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

for TYPE in $(ls -d docs/*/ | grep -v 'sample\|contributors\|antibodies'); do # Just get subdirectories
  TYPE=`basename $TYPE`
  [ $TYPE = 'sample' ] && echo 'Skip!' && continue # Sample metadata handled separately!
  echo "Testing $TYPE generation..."

  REAL_DEST="docs/$TYPE"
  TEST_DEST="docs-test/$TYPE"

  REAL_CMD="src/generate_docs.py $TYPE $REAL_DEST"
  TEST_CMD="src/generate_docs.py $TYPE $TEST_DEST"

  mkdir -p $TEST_DEST || echo "$TEST_DEST already exists"
  eval $TEST_CMD
  # TODO: Excel files contain a timestamp internally, in docProps/core.xml.
  # So, for now, there can be a mismatch that does not cause a failure.
  diff -r $REAL_DEST $TEST_DEST --exclude='*.xlsx' \
    || die "Update needed: $REAL_CMD
Or:" 'for D in `ls -d docs/*/  | grep -v "sample\|contributors\|antibodies"`; do src/generate_docs.py `basename $D` $D; done'
  rm -rf $TEST_DEST
  ((++GENERATE_COUNT))
done
[[ $GENERATE_COUNT -gt 0 ]] || die "No files generated"
