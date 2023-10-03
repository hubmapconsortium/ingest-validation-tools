#!/usr/bin/env bash
# Tests are run in offline by default. To test CEDAR validation including API calls, run:
# ./tests-manual/test-dataset-examples-cedar.sh <airflow_token> <cedar_api_token>

set -o errexit

die() { set +v; echo "$*" 1>&2 ; sleep 1; exit 1; }

for SUITE in examples/dataset-examples examples/dataset-iec-examples; do

    case $SUITE in
        examples/dataset-examples)
            OPTS="--dataset_ignore_globs 'ignore-*.tsv' '.*' --airflow_token $1 --cedar_api_key $2 --upload_ignore_globs 'drv_ignore_*' --output as_md"
            ;;
        *)
            die "Unexpected $SUITE"
    esac

    for EXAMPLE in $SUITE/*; do
        echo "Testing $EXAMPLE ..."
        CMD="src/validate_upload.py --local_directory $EXAMPLE/upload $OPTS | perl -pne 's/(Time|Git version): .*/\1: WILL_CHANGE/'"
        echo "$CMD"
        README="$EXAMPLE/README_ONLINE.md"
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
