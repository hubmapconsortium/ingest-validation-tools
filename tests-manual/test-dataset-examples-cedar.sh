#!/usr/bin/env bash
set -o errexit

die() { set +v; echo "$*" 1>&2 ; sleep 1; exit 1; }

GLOBUS_TOKEN=${1:?"Error. You must supply a globus token."}
START_INDEX=${2:-0}
INDEX=0

for SUITE in examples/dataset-examples examples/dataset-iec-examples; do

    case ${SUITE} in
        examples/dataset-iec-examples)
            OPTS="--dataset_ignore_globs 'metadata.tsv' --globus_token ${GLOBUS_TOKEN} --upload_ignore_globs '*' --run_plugins"
            ;;
        examples/dataset-examples)
            OPTS="--dataset_ignore_globs 'ignore-*.tsv' '.*' --run_plugins --globus_token ${GLOBUS_TOKEN} --upload_ignore_globs 'drv_ignore_*' --output as_md"
            ;;
        *)
            die "Unexpected ${SUITE}"
    esac

    for EXAMPLE in "${SUITE}"/*; do
        ((INDEX=INDEX+1))
        if [ "$INDEX" -lt "$START_INDEX" ]; then
            echo "Skipping ${INDEX}: ${SUITE}/${EXAMPLE}"
            continue
        fi
        README="${EXAMPLE}/README_ONLINE.md"
        echo "Testing ${INDEX}: ${EXAMPLE} ..."
        CMD="src/validate_upload.py --local_directory ${EXAMPLE}/upload ${OPTS} | perl -pne 's/(Time|Git version): .*/\1: WILL_CHANGE/'"
        echo "$CMD"
        if [ ! -e "${README}" ]; then
            echo "Example ${EXAMPLE} does not have a README_ONLINE.md file."
            die "Update example: ${CMD} > ${README}"
        fi
        diff "${README}" <( eval "${CMD}" ) \
            || die "Update example: ${CMD} > ${README}"
    done

    for GOOD in "${SUITE}"/good-*/README.md; do
        grep 'No errors!' "${GOOD}" > /dev/null || die "${GOOD} should not be an error report."
    done

    for BAD in "${SUITE}"/bad-*/README.md; do
        ! grep 'No errors!' "${BAD}" || die "${BAD} should be an error report."
    done

    echo "Done with ${SUITE}! No errors!"

done
