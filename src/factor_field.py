#!/usr/bin/env python3

import sys
import argparse
from pathlib import Path
import fileinput
from collections import defaultdict


def main():
    parser = argparse.ArgumentParser(description='''
    Factor out all variants of a given field.
    ''')
    parser.add_argument(
        '--field',
        metavar='NAME',
        required=True)
    parser.add_argument(
        '--input_dir',
        type=Path,
        metavar='IN',
        help='Directory to scan for instances of the field',
        default='src/ingest_validation_tools/table-schemas/assays')
    parser.add_argument(
        '--output_dir',
        type=Path,
        metavar='OUT',
        help='Directory to write field extracts',
        default='src/ingest_validation_tools/table-schemas/includes/fields')
    args = parser.parse_args()

    factor_field(args.field, args.input_dir, args.output_dir)
    return 0


def factor_field(field_name, input_dir, output_dir):
    definitions = pull(field_name, input_dir)
    push(field_name, definitions, output_dir)


def pull(field_name, input_dir):
    definitions = defaultdict(set)
    files = [str(f) for f in input_dir.iterdir()]
    with fileinput.input(files=files, inplace=True) as lines:
        replace(
            lines=lines,
            get_file_name=lambda: str(fileinput.filename()),
            field_name=field_name,
            definitions=definitions
        )
    return definitions


def push(field_name, definitions, output_dir):
    options = [
        f"# {'; '.join(sorted(files))}\n{definition}"
        for definition, files in definitions.items()
    ] if len(definitions) > 1 else definitions.keys()
    if options:
        (output_dir / f'{field_name}.yaml').write_text('\n'.join(options))
    else:
        print(f"Check spelling of field name: '{field_name}'")
        sys.exit(1)


def replace(lines, get_file_name, field_name, definitions):
    '''
    >>> lines = """
    ... - name: a
    ...   description: alpha
    ... - name: b
    ...   description: beta
    ... - name: c
    ...   description: gamma?
    ... """.split('\\n')
    >>> lines = [l + '\\n' for l in lines]
    >>> definitions = defaultdict(set)

    >>> replace(lines, get_file_name=lambda: 'fake.yaml', field_name='b', definitions=definitions)
    <BLANKLINE>
    - name: a
      description: alpha
    # include: ../includes/fields/b.yaml
    - name: c
      description: gamma?
    <BLANKLINE>

    >>> dict(definitions)
    {'- name: b\\n  description: beta\\n': {'fake.yaml'}}
    '''

    inside = False
    definition = None
    for line in lines:
        # This assumes the YAML has been cleaned up!
        if f'name: {field_name}' in line:
            inside = True
            print(f'# include: ../includes/fields/{field_name}.yaml')
            definition = line
            continue
        elif inside and line[0] not in ['-', '#']:
            definition += line
            continue
        elif inside:
            definitions[definition].add(get_file_name())
            inside = False
        print(line, end='')


if __name__ == "__main__":
    sys.exit(main())
