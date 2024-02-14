#!/usr/bin/env bash
set -o errexit

die() { set +v; echo "$red$*$reset" 1>&2 ; exit 1; }

PRE=src/ingest_validation_tools

for TABLE_SCHEMA in $PRE/table-schemas/level-2/*; do
  BASENAME=`basename $TABLE_SCHEMA`
  STEM="${BASENAME%.*}"
  ls $PRE/directory-schemas/${STEM}.yaml \
    || ls $PRE/directory-schemas/${STEM}-*.yaml \
    || die "Missing directory schema: echo 'items: {} # TODO' > $PRE/directory-schemas/${STEM}.yaml"
done
