#!/usr/bin/env bash
set -o errexit

die() { set +v; echo "$red$*$reset" 1>&2 ; exit 1; }

for FIXTURE in table-examples/*; do
  echo $FIXTURE
  EXPECTED="$FIXTURE/output.txt"
  ACTUAL="/tmp/actual-output.txt"
  CMD="python src/ingest_validation_tools/table_validator.py --fixture $FIXTURE"
  echo "Running: $CMD"
  $CMD > $ACTUAL
  diff $ACTUAL $EXPECTED || die "Mismatch: To fix: $CMD > $EXPECTED"
done