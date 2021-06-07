#!/usr/bin/env bash
set -o errexit

die() { set +v; echo "$red$*$reset" 1>&2 ; exit 1; }

DOCS='script-docs'
for TOOL in src/*.py; do
  TOOL=`basename $TOOL`
  echo "Testing $TOOL docs..."
  [ -e src/$TOOL ] || die "src/$TOOL does not exist."
  diff \
        <(perl -ne 'print if /usage: '$TOOL'/../```/ and ! /```/' $DOCS/README-$TOOL.md) \
        <(src/$TOOL -h) \
      || die 'Update: (echo '"'"'```text'"'"'; src/'$TOOL' -h; echo '"'"'```'"'"') >' $DOCS/README-$TOOL.md
done
