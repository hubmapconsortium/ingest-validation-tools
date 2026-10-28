#!/usr/bin/env bash
# Run offline tests (except those in tests/manual)
# Example usage:
# Run all tests with linting/formatting:
#   ./test.sh
# Run tests, skip linting/formatting:
#   ./test.sh -n
# Run tests, skip doc generation:
#   ./test.sh -d
# Run tests, skip linting/formatting and doc generation:
#   ./test.sh -nd
# Help:
#   ./test.sh --help

usage() { echo "Usage: $0 [-n] [-t <test_string>]
    -n : skip linting/formatting
    -d : skip doc generation" 1>&2; exit 1; }

# Define expected options
while getopts "nd" opt; do
	case "$opt" in
		n)
			echo "Skipping linting/formatting"
            SKIP_LF="$1"
		;;
		d)
			echo "Skipping doc generation"
            SKIP_D="$1"
		;;
        ?)
            usage
        ;;
	esac
done
shift $((OPTIND - 1))

# Run linting/formatting if not skipped with -n
# Respects configs in pyproject.toml / .flake8
# Note: black/isort will auto-format
if [ -z "$SKIP_LF" ]; then
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

# Run test-basic.sh
if [ -z $HALT ]; then
    echo "--------"
    ls tests/test-basics.sh | parallel --halt now,fail=1 bash
    if [ $? -ne 0 ]; then
        echo "Fix errors!"
        exit 1
    echo "--------"
    fi

    if [ -z "$SKIP_D" ]; then
        echo "Running doc generation..."
        echo "--------"
        ls tests/test-generate-docs.sh | parallel --halt now,fail=1 bash
        if [ $? -ne 0 ]; then
            echo "Fix errors!"
            exit 1
        fi
    echo "--------"
    fi

    echo "Running unittests..."
    echo "--------"
    python -m unittest tests/*.py
fi
