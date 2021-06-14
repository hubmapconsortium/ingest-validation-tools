#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path

from ingest_validation_tools.upload import get_schema_version


def make_parser():
    parser = argparse.ArgumentParser(
        description='''
Given an assay TSV, determines its type, and for each field with an ontology mapping,
adds an additional column with the URI that corresponds to the supplied term,
and prints the result to STDOUT.''')
    parser.add_argument('--path', type=Path)
    return parser


def main():
    parser = make_parser()
    args = parser.parse_args()
    expanded_tsv = get_expanded_tsv(args.path)
    print(expanded_tsv)
    return 0


def get_expanded_tsv(path):
    get_schema_version(path)
    # TODO:
    # - Get the schema
    # - Read the input TSV
    # - For each line in the TSV, print it out again,
    #   expanding columns with dict enums.


if __name__ == "__main__":
    exit_status = main()
    sys.exit(exit_status)
