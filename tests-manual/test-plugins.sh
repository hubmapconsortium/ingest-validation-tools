#!/usr/bin/env bash
set -o errexit

die() { set +v; echo "$*" 1>&2 ; sleep 1; exit 1; }

for EXAMPLE in examples/plugin-tests/*; do
    OPTS="--dataset_ignore_globs 'ignore-*.tsv' '.*' --upload_ignore_globs 'drv_ignore_*' --offline --run_plugins --plugin_directory ../ingest-validation-tests/src/ingest_validation_tests/ --output as_md"
    echo "Testing $EXAMPLE ..."
    CMD="src/validate_upload.py --local_directory $EXAMPLE/upload $OPTS | perl -pne 's/(Time|Git version): .*/\1: WILL_CHANGE/'"
    echo "$CMD"
    README="$EXAMPLE/README.md"
    # ingest-validation-tests spits out extra output that is inconsistent; these regex strings skip that bit and only check output
    [[ $(eval $CMD) =~ \`\`\`(.|\n)*\`\`\` ]]
    TRUNC_CMD=${BASH_REMATCH[0]}
    TRUNC_README=$(grep -Pzo '```(.|\n)+' $README | head -c-1)
    diff <(echo "$TRUNC_README") <(echo "$TRUNC_CMD") \
        || die "Update example: $CMD > $README"

    echo "No errors!"
done
