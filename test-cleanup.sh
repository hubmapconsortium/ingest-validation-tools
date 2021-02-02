#!/usr/bin/env bash
set -o errexit

die() { set +v; echo "$*" 1>&2 ; exit 1; }

for ENCODING in ascii utf-8 latin-1; do
  echo "Testing $ENCODING..."
  WEIRD_TSV=cleanup-examples/$ENCODING.input.tsv
  src/cleanup_whitespace.py --encoding_test $ENCODING > $WEIRD_TSV
  src/cleanup_whitespace.py --tsv_path $WEIRD_TSV > cleanup-examples/$ENCODING.clean.tsv
  diff cleanup-examples/$ENCODING.clean.tsv cleanup-examples/expected.tsv \
  || die "Not the expected output"
done