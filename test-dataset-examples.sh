#!/usr/bin/env bash
set -o errexit

red=`tput setaf 1`
reset=`tput sgr0`
die() { set +v; echo "$red$*$reset" 1>&2 ; exit 1; }

for SUITE in dataset-iec-examples dataset-examples; do

  case $SUITE in
    dataset-iec-examples)
      OPTS="--dataset_ignore_globs 'metadata.tsv' --submission_ignore_globs '*' --output as_text_list"
      ;;
    dataset-examples)
      # To minimize dependence on outside resources, --offline used here,
      # but ID lookup is still exercised by iec-examples.
      OPTS="--dataset_ignore_globs 'ignore-*.tsv' '.*' --submission_ignore_globs 'drv_ignore_*' --offline --output as_md"
      ;;
    *)
      die "Unexpected $SUITE"
  esac

  for EXAMPLE in $SUITE/*; do
    echo "Testing $EXAMPLE ..."
    CMD="src/validate_submission.py --local_directory $EXAMPLE/submission $OPTS "
    echo "$CMD"
    README="$EXAMPLE/README.md"
    diff $README <( eval "$CMD" ) \
      || die "Update example: $CMD > $README"
  done

  for GOOD in $SUITE/good-*/README.md; do
    grep 'No errors!' $GOOD > /dev/null || die "$GOOD should not be an error report."
  done

  for BAD in $SUITE/bad-*/README.md; do
    ! grep 'No errors!' $BAD || die "$BAD should be an error report."
  done

done
