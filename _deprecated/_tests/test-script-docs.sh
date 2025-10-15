#!/usr/bin/env bash
set -o errexit

die() { set +v; echo "$red$*$reset" 1>&2 ; exit 1; }

DOCS='script-docs'
for TOOL in src/*.py; do
  TOOL=`basename $TOOL`
  echo "Testing $TOOL docs..."
  [ -e src/$TOOL ] || die "src/$TOOL does not exist."

  # In python 3.10, this string changed.
  # Since we want the doc build to be the same in all environments, use perl to search and replace.
  DOC_CMD="src/$TOOL -h | perl -pne 's/options:/optional arguments:/'"

  perl -ne 'print if /usage: '$TOOL'/../```/ and ! /```/' $DOCS/README-$TOOL.md > /tmp/expected.txt
  eval $DOC_CMD > /tmp/actual.txt

  diff /tmp/expected.txt /tmp/actual.txt \
      || die 'Update: (echo '"'"'```text'"'"'; '$DOC_CMD'; echo '"'"'```'"'"') >' $DOCS/README-$TOOL.md
done
