#!/usr/bin/env bash
set -o errexit

die() { set +v; echo "$red$*$reset" 1>&2 ; exit 1; }

for FIXTURE in examples/custom-constraint-examples/*; do
  echo $FIXTURE
  EXPECTED="$FIXTURE/output.txt"
  ACTUAL="/tmp/actual-output.txt"
  CMD="PYTHONPATH=src:\$PYTHONPATH python3 src/ingest_validation_tools/local_validation/table_validator.py --fixture $FIXTURE"
  echo "Running: $CMD"
  eval $CMD > $ACTUAL
  diff $EXPECTED $ACTUAL || die "To fix: $CMD > $EXPECTED"
done
