#!/usr/bin/env bash
# Example usage:
# Run specific test (will not proceed if linting/formatting errors):
#   ./test.sh -t tests.test_single_tsv.TestSingleTsv.test_bad_payload
# Same as above, skipping linting/formatting:
#   ./test.sh -n -t tests.test_single_tsv.TestSingleTsv.test_bad_payload
# Run all tests except plugin tests, skip linting/formatting:
#   ./test.sh -n
# Run all tests including plugin tests, skip linting/formatting:
#   ./test.sh -n -p
# Run all tests, pass arbitrary argument directly to unittest:
#   ./test.sh -- hello_unittest

usage() { echo "Usage: $0 [-n] [-t <test_string>]
    -n : skip linting/formatting
    -t : run specific test; use unittest format
        example: tests.test_single_tsv.TestSingleTsv.test_bad_payload
    -p : run plugins; requires ingest-validation-tests
    -- pass arbitrary other args following ' -- '" 1>&2; exit 1; }

# Define expected options
while getopts "nt:p" opt; do
	case "$opt" in
		n)
			echo "Skipping linting/formatting"
            SKIP="$1"
		;;
		t)
            if [[ "$OPTARG" = "--" ]]; then
                echo "-t must be followed by reference to a test"
                usage
            else
                TEST="$OPTARG"
            fi
        ;;
		p)
			echo "Running plugin tests"
            PLUGINS="$1"
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
    echo "Fix linting/formatting errors or pass -n/-no_lint to run tests."
    exit 1
fi

# Run test scripts, exit on first failure to avoid burying error messages
echo "--------"
ls tests/*.sh | parallel --halt now,fail=1 bash
if [ $? -ne 0 ]; then
    echo "Fix errors!"
    exit
fi

# Run python tests
echo "--------"
PYTHONPATH=/ingest-validation-tools
python -m unittest tests.test_single_tsv tests.test_dataset_examples
if [ $PLUGINS ]; then
    echo "Running plugin tests"
    python -m unittest tests.manual.test_plugins
fi
