#!/usr/bin/env python
import sys
from pathlib import Path
from yaml import safe_load as load_yaml


def get_search_api_assay_types():
    assay_types_path = (
        Path(__file__).parent /
        'src/search-api/src/search-schema/data' /
        'definitions/enums/assay_types.yaml')
    assay_types_info = load_yaml(assay_types_path.read_text())
    return [v['description'] for v in assay_types_info.values()]


def get_level_1_assay_types():
    level_1_path = (
        Path(__file__).parent /
        'src/ingest_validation_tools/table-schemas' /
        'level-1.yaml')
    level_1_info = load_yaml(level_1_path.read_text())
    assay_type_matches = [
        f for f in level_1_info['fields']
        if f['name'] == 'assay_type'
    ]
    assert len(assay_type_matches) == 1, \
        f'Expected one match, not {assay_type_matches}'
    return assay_type_matches[0]['constraints']['enum']


def main():
    search_api_assays = set(get_search_api_assay_types())
    level_1_assays = set(get_level_1_assay_types())
    level_1_but_not_search_api = level_1_assays - search_api_assays
    if level_1_but_not_search_api:
        print(f'level-1 but not search-api: {level_1_but_not_search_api}')
        sys.exit(1)


if __name__ == "__main__":
    main()
