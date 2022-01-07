#!/usr/bin/env python3

import argparse
from pathlib import Path
import sys
from yaml import dump as dump_yaml, safe_load

from tableschema_to_template.create_xlsx import create_xlsx

from ingest_validation_tools.schema_loader import (
    dict_schema_versions, get_table_schema, get_other_schema, get_directory_schema,
    get_pipeline_infos, get_is_assay, enum_maps_to_lists)
from ingest_validation_tools.docs_utils import (
    get_tsv_name, get_xlsx_name,
    generate_template_tsv, generate_readme_md)
from ingest_validation_tools.cli_utils import dir_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'target',
        type=Path,
        help='Path for MD file')
    args = parser.parse_args()

    field_schemas = safe_load(
        (Path(__file__).parent.parent / 'docs/field-schemas.yaml').read_text()
    )

    all_schemas = set()
    for schemas in field_schemas.values():
        all_schemas |= set(schemas)
    
    schema_cols = list(all_schemas)

    with open(args.target, 'w') as f:
        f.write(
'''---
layout: default
title: HuBMAP Data Upload Guidelines
---
''')
        f.write(' '.join(schema_cols))
        for field, schemas in field_schemas.items():
            f.write(field)
            cols = ['X' if schema in schemas else ' ' for schema in schema_cols]
            f.write(' '.join(cols))


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
