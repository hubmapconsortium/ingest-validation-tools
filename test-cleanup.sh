#!/usr/bin/env bash
set -o errexit

die() { set +v; echo "$*" 1>&2 ; exit 1; }

for FIXTURE in cleanup-examples/*; do
  [[ "$FIXTURE" == *".clean."* ]] && continue
  echo "Testing $FIXTURE"
  STEM="${FIXTURE%.*}"
  CLEAN="$STEM.clean.tsv"
  src/cleanup_whitespace.py $FIXTURE > $CLEAN
  PAIR="$CLEAN $STEM.clean.expected.tsv"
  diff $PAIR \
  || die "To silence error: cp $PAIR"
done