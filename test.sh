#!/usr/bin/env bash
set -o errexit

ls tests/*.sh | parallel --halt now,fail=1 bash
PYTHONPATH=/ingest-validation-tools
python -m unittest tests/test-dataset-examples.py
