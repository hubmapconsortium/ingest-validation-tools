#!/usr/bin/env python3

import sys
import argparse
from pathlib import Path

from yaml import safe_load


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--dir_schema',
        type=Path,
        required=True,
        help='Directory schema file')
    parser.add_argument(
        '--target',
        type=Path,
        required=True,
        help='Target directory to populate')
    args = parser.parse_args()

    schema = safe_load(args.dir_schema.read_text())
    for entry in schema:
        if 'example' not in entry:
            print(f'No example for {entry["pattern"]}')
            continue
        new_path = args.target / entry['example']
        new_path.parent.mkdir(parents=True, exist_ok=True)
        new_path.touch()
        print(f'Created {new_path}')
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
