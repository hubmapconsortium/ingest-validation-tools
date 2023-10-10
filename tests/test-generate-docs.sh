#!/usr/bin/env bash
set -o errexit

die() { set +v; echo "$*" 1>&2 ; sleep 1; exit 1; }

# Test field-descriptions.yaml and field-types.yaml:

ATTR_LIST='description type entity assay schema'
RERUNS=''
for ATTR in $ATTR_LIST; do
  PLURAL="${ATTR}s"
  [ "$PLURAL" == 'entitys' ] && PLURAL='entities'
  REAL_DEST="docs/field-${PLURAL}.yaml"
  TEST_DEST="docs-test/field-${PLURAL}.yaml"
  echo "Checking $REAL_DEST"

  REAL_CMD="src/generate_field_yaml.py --attr $ATTR > $REAL_DEST;"
  TEST_CMD="src/generate_field_yaml.py --attr $ATTR > $TEST_DEST"

  mkdir docs-test || echo "Already exists"
  eval $TEST_CMD || die "Command failed: $TEST_CMD"
  diff -r $REAL_DEST $TEST_DEST || RERUNS="$RERUNS $REAL_CMD"
  rm -rf docs-test
done
[ -z "$RERUNS" ] || die "Update YAMLs: $RERUNS"

# Test Excel summary:
# This relies on the YAML created above.

FILE="field-schemas.xlsx"
echo "Checking $FILE"

mkdir docs-test
REAL_DEST="docs/$FILE"
TEST_DEST="docs-test/$FILE"
REAL_CMD="src/generate_grid.py $REAL_DEST"
TEST_CMD="src/generate_grid.py $TEST_DEST"
eval $TEST_CMD || die "Command failed: $TEST_CMD"
diff $REAL_DEST $TEST_DEST || die "Update needed: $REAL_CMD"

# Test docs:

for TYPE in $(ls -d docs/*); do
  # Skip directories that are unpopulated:
  TYPE=`basename $TYPE`
  LOOKFOR_CURRENT_ASSAY="docs/$TYPE/current/$TYPE-metadata.tsv"
  LOOKFOR_CURRENT_OTHER="docs/$TYPE/current/$TYPE.tsv"
  LOOKFOR_DEPRECATED_ASSAY="docs/$TYPE/deprecated/$TYPE-metadata.tsv"
  LOOKFOR_DEPRECATED_OTHER="docs/$TYPE/deprecated/$TYPE.tsv"
  if [ ! -e $LOOKFOR_CURRENT_ASSAY ] && [ ! -e $LOOKFOR_CURRENT_OTHER ] && [ ! -e $LOOKFOR_DEPRECATED_ASSAY ] && [ ! -e $LOOKFOR_DEPRECATED_OTHER ]; then
    echo "Skipping $TYPE. To add: 'touch $LOOKFOR_CURRENT_ASSAY' for assays, or 'touch $LOOKFOR_CURRENT_OTHER' for other."
    continue
  fi

  echo "Testing $TYPE generation..."

  REAL_DEST="docs/$TYPE"
  TEST_DEST="docs-test/$TYPE"

  REAL_CMD="src/generate_docs.py $TYPE $REAL_DEST"
  TEST_CMD="src/generate_docs.py $TYPE $TEST_DEST"

  mkdir -p $TEST_DEST || echo "$TEST_DEST already exists"
  echo "Running: $TEST_CMD"
  eval $TEST_CMD

  if [ -e $REAL_DEST/current ] && [ -e $TEST_DEST/current ]; then
    diff -r $REAL_DEST/current $TEST_DEST/current --exclude="*.tsv" --exclude="*.xlsx" \
      || die "Update needed: $REAL_CMD
  Or:" 'for D in `ls -d docs/*/`; do D=`basename $D`; [ -e docs/$D/*.tsv ] || continue; src/generate_docs.py $D docs/$D; done'
  fi

  if [ -e $REAL_DEST/deprecated ] && [ -e $TEST_DEST/deprecated ]; then
    diff -r $REAL_DEST/deprecated $TEST_DEST/deprecated --exclude="*.tsv" --exclude="*.xlsx" \
      || die "Update needed: $REAL_CMD
  Or:" 'for D in `ls -d docs/*/`; do D=`basename $D`; [ -e docs/$D/*.tsv ] || continue; src/generate_docs.py $D docs/$D; done'
  fi

  rm -rf $TEST_DEST
  ((++GENERATE_COUNT))
done
[[ $GENERATE_COUNT -gt 0 ]] || die "No files generated"
