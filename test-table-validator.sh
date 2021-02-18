#!/usr/bin/env bash
set -o errexit

die() { set +v; echo "$red$*$reset" 1>&2 ; exit 1; }

for FIXTURE in table-examples/*; do
  echo $FIXTURE
  INPUT_TSV="$FIXTURE/input.tsv"
  SCHEMA="$FIXTURE/schema.yaml"
  EXPECTED="$FIXTURE/output.txt"
  ACTUAL="/tmp/actual-output.txt"
  PARAMS="--tsv_path $INPUT_TSV --schema_path $SCHEMA"
  CMD="python src/ingest_validation_tools/table_validator.py $PARAMS"
  echo "Running : $CMD"
  $CMD > $ACTUAL
  diff $ACTUAL $EXPECTED || die "Mismatch: To fix: $CMD > $EXPECTED"
done