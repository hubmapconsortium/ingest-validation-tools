#!/usr/bin/env bash
set -o errexit

die() { set +v; echo "$*" 1>&2 ; sleep 1; exit 1; }

GLOBUS_TOKEN=${1:?"Error. You must supply a globus token."}
CEDAR_API_KEY=${2:?"Error. You must supply a CEDAR API key."}

for SUITE in examples/dataset-examples; do

    case ${SUITE} in
        examples/dataset-examples)
            OPTS="--dataset_ignore_globs 'ignore-*.tsv' '.*' --globus_token ${GLOBUS_TOKEN} --cedar_api_key ${CEDAR_API_KEY} --upload_ignore_globs 'drv_ignore_*' --output as_md"
            ;;
        *)
            die "Unexpected ${SUITE}"
    esac

    for EXAMPLE in "${SUITE}"/*; do
        README="${EXAMPLE}/README_ONLINE.md"
        if [ ! -e "${README}" ]; then
            if [[ "${EXAMPLE}" == *cedar* ]];  then
                die "CEDAR example ${EXAMPLE} does not have a README_ONLINE.md file."
            fi
        else
            echo "Testing ${EXAMPLE} ..."
            CMD="src/validate_upload.py --local_directory ${EXAMPLE}/upload ${OPTS} | perl -pne 's/(Time|Git version): .*/\1: WILL_CHANGE/'"
            echo "$CMD"
            diff "${README}" <( eval "${CMD}" ) \
                || die "Update example: ${CMD} > ${README}"
        fi
    done

    for GOOD in "${SUITE}"/good-*/README.md; do
        grep 'No errors!' "${GOOD}" > /dev/null || die "${GOOD} should not be an error report."
    done

    for BAD in "${SUITE}"/bad-*/README.md; do
        ! grep 'No errors!' "${BAD}" || die "${BAD} should be an error report."
    done

    echo "Done! No errors!"

done
