#!/usr/bin/env python3

import argparse
import sys


def make_parser():
    return argparse.ArgumentParser(
        description='''
Given an assay TSV on STDIN, determines its type, and for each field with an ontology mapping,
adds an additional column with the URI that corresponds to the supplied term,
and prints the result to STDOUT.''')


def main():
    parser = make_parser()
    args = parser.parse_args()

    print(args)
    # TODO
    return 0


if __name__ == "__main__":
    exit_status = main()
    sys.exit(exit_status)
