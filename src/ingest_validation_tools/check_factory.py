import re
from string import Template
import shelve
from pathlib import Path
from sys import stderr

import frictionless
import requests


cache_path = str(Path(__file__).parent / 'url-status-cache')


class CheckFactory():
    def __init__(self, schema):
        self.schema = schema
        self._prev_value_run_length = {}

    def _get_constrained_fields(self, constraint):
        c_c = 'custom_constraints'
        return {
            f['name']: f[c_c][constraint] for f in self.schema['fields']
            if c_c in f and constraint in f[c_c]
        }

    def _check_url_status_cache(self, url):
        with shelve.open(cache_path) as url_status_cache:
            if url not in url_status_cache:
                print(f'Fetching un-cached url: {url}', file=stderr)
                response = requests.get(url)
                url_status_cache[url] = response.status_code
            return url_status_cache[url]

    def make_url_check(self, template=Template(
            'URL returned $status: "$url"')):
        url_constrained_fields = self._get_constrained_fields('url')

        def url_check(row):
            for k, v in row.items():
                if v is None:
                    continue
                if k in url_constrained_fields:
                    prefix = url_constrained_fields[k]['prefix']
                    url = f'{prefix}{v}'
                    status = self._check_url_status_cache(url)
                    if status != 200:
                        note = template.substitute(status=status, url=url)
                        yield frictionless.errors.CellError.from_row(row, note=note, field_name=k)
        return url_check

    def make_sequence_limit_check(self, template=Template(
            'there is a run of $run_length sequential items: Limit is $limit. '
            'If correct, reorder rows.')):
        sequence_limit_fields = self._get_constrained_fields('sequence_limit')

        def sequence_limit_check(row):
            prefix_number_re = r'(?P<prefix>.*?)(?P<number>\d+)$'
            for k, v in row.items():
                # If the schema declares the field as datetime,
                # "v" will be a python object, and regexes will error.
                v = str(v)

                if k not in sequence_limit_fields or not v:
                    continue

                match = re.search(prefix_number_re, v)
                if not match:
                    if k in self._prev_value_run_length:
                        del self._prev_value_run_length[k]
                    continue

                if k not in self._prev_value_run_length:
                    self._prev_value_run_length[k] = (v, 1)
                    continue

                prev_value, run_length = self._prev_value_run_length[k]
                prev_match = re.search(prefix_number_re, prev_value)
                if (
                    match.group('prefix') != prev_match.group('prefix') or
                    int(match.group('number')) != int(prev_match.group('number')) + 1
                ):
                    self._prev_value_run_length[k] = (v, 1)
                    continue

                run_length += 1
                self._prev_value_run_length[k] = (v, run_length)

                limit = sequence_limit_fields[k]
                assert limit > 1, 'The lowest allowed limit is 2'
                if run_length >= limit:
                    note = template.substitute(run_length=run_length, limit=limit)
                    yield frictionless.errors.CellError.from_row(row, note=note, field_name=k)

        return sequence_limit_check

    def make_units_check(self, template=Template(
            'Required when $units_for is filled')):
        units_constrained_fields = self._get_constrained_fields('units_for')

        def units_check(row):
            for k, v in row.items():
                if k in units_constrained_fields:
                    units_for = units_constrained_fields[k]
                    if (row[units_for] or row[units_for] == 0) and not row[k]:
                        note = template.substitute(units_for=units_for)
                        yield frictionless.errors.CellError.from_row(row, note=note, field_name=k)
        return units_check
