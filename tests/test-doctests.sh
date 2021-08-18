#!/usr/bin/env bash
set -o errexit

cd src

DOCTESTS=`find . | grep '\.py$'`
for TEST in $DOCTESTS; do
  CMD="python3 -m doctest $TEST"
  # doctest by itself is silent on success.
  echo 'cd src;' $CMD
  $CMD
done
