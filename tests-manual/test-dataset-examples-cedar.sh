#!/usr/bin/env bash
# Tests are run in offline by default. To test CEDAR validation including API calls, run:
# ./tests-manual/test-dataset-examples-cedar.sh <globus_token> <cedar_api_token>
# This means all examples with CEDAR API validation will need a README_ONLINE.md file; this will try to detect a missing but necessary file based on example names including the string "cedar"

set -o errexit

die() { set +v; echo "$*" 1>&2 ; sleep 1; exit 1; }

for SUITE in examples/dataset-examples; do

    case $SUITE in
        examples/dataset-examples)
            OPTS="--dataset_ignore_globs 'ignore-*.tsv' '.*' --globus_token $1 --cedar_api_key $2 --upload_ignore_globs 'drv_ignore_*' --output as_md"
            ;;
        *)
            die "Unexpected $SUITE"
    esac

    for EXAMPLE in $SUITE/*; do
        README="$EXAMPLE/README_ONLINE.md"
        if [ ! -e "$README" ]; then
            if [[ "$EXAMPLE" == *cedar* ]];  then
                die "CEDAR example $EXAMPLE does not have a README_ONLINE.md file."
            fi
        else
            echo "Testing $EXAMPLE ..."
            CMD="src/validate_upload.py --local_directory $EXAMPLE/upload $OPTS | perl -pne 's/(Time|Git version): .*/\1: WILL_CHANGE/'"
            echo "$CMD"
            diff $README <( eval "$CMD" ) \
                || die "Update example: $CMD > $README"
        fi
    done

    for GOOD in $SUITE/good-*/README.md; do
        grep 'No errors!' $GOOD > /dev/null || die "$GOOD should not be an error report."
    done

    for BAD in $SUITE/bad-*/README.md; do
        ! grep 'No errors!' $BAD || die "$BAD should be an error report."
    done

    echo "Done! No errors!"

done
