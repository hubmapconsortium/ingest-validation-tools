#!/usr/bin/env python

import argparse
import sys
import os

from validator import validate


def main():
    # parser = argparse.ArgumentParser()
    # args = parser.parse_args()
    validate('foo', 'bar') # TODO
    return 1


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
