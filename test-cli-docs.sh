#!/usr/bin/env bash
set -o errexit

die() { set +v; echo "$red$*$reset" 1>&2 ; exit 1; }

for TOOL in src/*.py; do
  TOOL=`basename $TOOL`
  [ "$TOOL" == 'generate_field_descriptions.py' ] && continue
  echo "Testing $TOOL docs..."
  [ -e src/$TOOL ] || die "src/$TOOL does not exist."
  diff \
        <(perl -ne 'print if /usage: '$TOOL'/../```/ and ! /```/' README-$TOOL.md) \
        <(src/$TOOL -h) \
      || die 'Update: (echo '"'"'```'"'"'; src/'$TOOL' -h; echo '"'"'```'"'"') >' README-$TOOL.md
done
