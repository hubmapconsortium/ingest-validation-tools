#!/usr/bin/env bash
# Example usage:
# Run all tests (offline) except plugins, with linting/formatting:
#   ./test.sh
# Run all tests (offline) except plugin tests, skip linting/formatting:
#   ./test.sh -n
# Run all tests including plugin tests (offline), skip linting/formatting:
#   ./test.sh -n -p
# Run all tests (excluding plugin tests), run example dir tests online, skip linting/formatting:
#   ./test.sh -n -o globus_token
# Run specific python unittest(s) only (skips linting/formatting check, other tests):
#   ./test.sh -t tests.test_single_tsv.TestSingleTsv.test_bad_payload
# Run one or more example dir tests only (offline):
#   ./test.sh -d examples/dataset-iec-examples/bad-example
# Run one or more example dir tests only (online):
#   ./test.sh -o globus_token -d examples/dataset-iec-examples/bad-example
# Run all tests, pass arbitrary argument directly to unittest:
#   ./test.sh -- hello_unittest
# Help:
#   ./test.sh --help

usage() { echo "Usage: $0 [-n] [-t <test_string>]
    -n : skip linting/formatting
    -t : run specific test (skip all others); use unittest format
         example: -t tests.test_single_tsv.TestSingleTsv.test_bad_payload
    -p : run plugins; requires ingest-validation-tests
    -o : run online, requires Globus token (omit `Bearer`)
    -d : test specific example directory (skip all others);
         provide path starting with examples/;
         runs in offline mode by default
         example: -d examples/dataset-iec-examples/bad-example
    -- pass arbitrary other args following ' -- '" 1>&2; exit 1; }

# Define expected options
while getopts "nt:po:d:" opt; do
	case "$opt" in
		n)
			echo "Skipping linting/formatting"
            SKIP="$1"
		;;
		t)
            echo "Running specified test(s): $OPTARG"
            TEST="$OPTARG"
            HALT=1
            SKIP="$1"
        ;;
		p)
			echo "Running plugin tests"
            PLUGINS="$1"
		;;
		o)
			echo "Running tests in online mode"
            GLOBUS_TOKEN="$OPTARG"
		;;
		d)
			echo "Attempting to test example dir $OPTARG"
            DIR="$OPTARG"
            HALT=1
            SKIP="$1"
		;;
        ?)
            usage
        ;;
	esac
done
shift $((OPTIND - 1))

# Define -- as delimiter between options and arbitrary args to pass to unittest
[[ $1 = "--" ]] && shift
PARAMS=("$PARAMS$@")

# If -t, just run specified test(s), skip everything else
if [ $TEST ]; then
    python -m unittest $TEST $PARAMS
    exit
fi

# Run linting/formatting if not skipped with -n
# Respects configs in pyproject.toml / .flake8
# Note: black/isort will auto-format
if [ -z "$SKIP" ]; then
    echo "Running linting/formatting checks..."
    echo "--------"
    echo "black"
    black src
    if [ $? -ne 0 ]; then
        ERROR=1
    fi
    echo "--------"
    echo "isort"
    isort src
    if [ $? -ne 0 ]; then
        ERROR=1
    fi
    echo "--------"
    echo "flake8"
    flake8 src
    if [ $? -ne 0 ]; then
        ERROR=1
    fi
fi

# Exit if linting/formatting errors found
if [[ $ERROR == 1 ]]; then
    echo "Fix linting/formatting errors or pass -n to run tests."
    exit 1
fi

# Run test scripts, exit on first failure to avoid burying error messages
if [ -z $HALT ]; then
    echo "--------"
    ls tests/*.sh | parallel --halt now,fail=1 bash
    if [ $? -ne 0 ]; then
        echo "Fix errors!"
        exit
    fi
fi

# Test example dirs. Only runs if dir is specified (-d <dir>) or if run in
# online mode (-o <token>); otherwise, dataset-examples and dataset-iec-examples
# are tested in Python test suite.
echo "--------"
PYTHONPATH=/ingest-validation-tools
TEST_DIRS="examples/dataset-examples examples/dataset-iec-examples"
if [ -v DIR ]; then
    TEST_DIRS=$DIR
fi
if [ $GLOBUS_TOKEN ]; then
    echo "Running online tests in dry_run mode"
    python -m tests.manual.update_test_data -t $TEST_DIRS -g $GLOBUS_TOKEN --dry_run -v
elif [ $DIR ]; then
    echo "Running offline tests in dry_run mode"
    python -m tests.manual.update_test_data -t $TEST_DIRS -g "" --dry_run --manual_test -v
fi
if [ $PLUGINS ]; then
    echo "Running plugin tests"
    python -m unittest tests.manual.test_plugins
fi

if [ -z $HALT ]; then
    echo "--------"
    # Run python tests
    python -m unittest tests/*.py
fi

