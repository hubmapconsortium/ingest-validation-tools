#!/usr/bin/env python3
import sys
from csv import DictWriter
import argparse
import re

import requests


def main():
    parser = argparse.ArgumentParser()

    default_url = 'https://search.api.hubmapconsortium.org/portal/search'
    parser.add_argument(
        '--url',
        default=default_url,
        help=f'ES endpoint. Default: {default_url}')

    default_size = 20
    parser.add_argument(
        '--size',
        type=int,
        default=default_size,
        help=f'Number of records to pull. Default: {default_size}')

    default_type = 'Dataset'
    parser.add_argument(
        '--type',
        default=default_type,
        help=f'Entity type to query. Default: {default_type}')

    args = parser.parse_args()

    query = {
        'post_filter': {'term': {'entity_type.keyword': args.type}},
        'size': args.size,
        '_source': ['metadata.metadata' if args.type == 'Dataset' else 'metadata']
    }
    response = requests.post(args.url, json=query)
    hits = response.json()['hits']['hits']

    writer = DictWriter(
        sys.stdout,
        fieldnames=[
            'uuid',
            'assay_type',
            'field',
            'value'],
        extrasaction='ignore')
    writer.writeheader()
    for hit in hits:
        uuid = hit['_id']

        if 'metadata' not in hit['_source']:
            continue
        meta = hit['_source']['metadata']

        if 'metadata' in meta:
            meta = meta['metadata']

        for field, value in meta.items():
            if not re.search(r'[A-Za-z]', value):
                continue
            writer.writerow({
                'uuid': uuid,
                'assay_type': meta['assay_type'] if 'assay_type' in meta else 'Sample',
                'field': field,
                'value': value
            })

    assert len(hits) < args.size, f'Result truncated at {args.size}'
    return 0


if __name__ == '__main__':
    sys.exit(main())  # pragma: no cover
