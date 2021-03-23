#!/usr/bin/env bash
set -o errexit

red=`tput setaf 1`
reset=`tput sgr0`
die() { set +v; echo "$red$*$reset" 1>&2 ; exit 1; }

for EXAMPLE in examples/sample-examples/*; do
  echo "Testing $EXAMPLE ..."
  CMD="src/validate_samples.py --path $EXAMPLE/sample.tsv --output as_md"
  echo "( $CMD )"
  README="$EXAMPLE/README.md"
  diff $README <( eval "$CMD" ) \
    || die "Update example: $CMD > $README"
done

for GOOD in examples/sample-examples/good-*/README.md; do
  grep 'No errors!' $GOOD > /dev/null || die "$GOOD should not be an error report."
done

for BAD in examples/sample-examples/bad-*/README.md; do
  ! grep 'No errors!' $BAD || die "$BAD should be an error report."
done
