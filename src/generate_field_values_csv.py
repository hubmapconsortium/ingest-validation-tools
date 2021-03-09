#!/usr/bin/env python3
import sys
from csv import DictWriter
import argparse
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
        default=default_size,
        help=f'Number of datasets to pull. Default: {default_size}')

    args = parser.parse_args()
    
    query = {
        'post_filter': {'term': {'entity_type.keyword': 'Dataset'}},
        'size': args.size,
        '_source': ['metadata.metadata']
    }
    response = requests.post(args.url, json=query)
    hits = response.json()['hits']['hits']

    writer = DictWriter(sys.stdout, fieldnames=['uuid', 'field', 'value'], extrasaction='ignore')
    writer.writeheader()
    for hit in hits:
        uuid = hit['_id']

        if 'metadata' not in hit['_source']: continue
        outer_meta = hit['_source']['metadata']
        
        if 'metadata' not in outer_meta: continue
        inner_meta = outer_meta['metadata']
        
        for field, value in inner_meta.items():
            writer.writerow({
                'uuid': uuid,
                'field': field,
                'value': value
            })

    assert len(hits) < args.size, f'Result truncated at {args.size}'
    return 0

if __name__ == '__main__':
    sys.exit(main())  # pragma: no cover
