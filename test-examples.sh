#!/usr/bin/env bash
set -o errexit

red=`tput setaf 1`
reset=`tput sgr0`
die() { set +v; echo "$red$*$reset" 1>&2 ; exit 1; }

for EXAMPLE in examples/*; do
  CMD="src/validate_submission.py --local_directory $EXAMPLE/submission"
  README="$EXAMPLE/README.md"
  diff $README <( $CMD ) \
    || die "Update example: $CMD > $README"
done
