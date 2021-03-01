import re

import frictionless
import requests


class CheckFactory():
    def __init__(self, schema):
        self.schema = schema
        self._url_status_cache = {}
        self._prev_value_run_length = {}

    def _get_constrained_fields(self, constraint):
        c_c = 'custom_constraints'
        return {
            f['name']: f[c_c][constraint] for f in self.schema['fields']
            if c_c in f and constraint in f[c_c]
        }

    def _check_url_status_cache(self, url):
        if url not in self._url_status_cache:
            response = requests.get(url)
            self._url_status_cache[url] = response.status_code
        return self._url_status_cache[url]

    def make_url_check(self):
        url_constrained_fields = self._get_constrained_fields('url')

        def url_check(row, schema=self.schema):
            for k, v in row.items():
                if v is None:
                    continue
                if k in url_constrained_fields:
                    prefix = url_constrained_fields[k]['prefix']
                    url = f'{prefix}{v}'
                    status = self._check_url_status_cache(url)
                    if status != 200:
                        note = f'URL returned {status}: {url}'
                        yield frictionless.errors.CellError.from_row(row, note=note, field_name=k)
        return url_check

    def make_sequence_limit_check(self):
        sequence_limit_fields = self._get_constrained_fields('sequence_limit')

        def sequence_limit_check(row, schema=self.schema):
            prefix_number_re = r'(?P<prefix>.*?)(?P<number>\d+)$'
            for k, v in row.items():
                if k not in sequence_limit_fields or not v:
                    continue

                match = re.search(prefix_number_re, v)
                if not match:
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
                if run_length >= limit:
                    note = f'incremented {run_length} times; limit is {limit}'
                    yield frictionless.errors.CellError.from_row(row, note=note, field_name=k)

        return sequence_limit_check

    def make_units_check(self):
        units_constrained_fields = self._get_constrained_fields('units_for')

        def units_check(row, schema=self.schema):
            for k, v in row.items():
                if k in units_constrained_fields:
                    units_for = units_constrained_fields[k]
                    if (row[units_for] or row[units_for] == 0) and not row[k]:
                        note = f'Required when {units_for} is filled'
                        yield frictionless.errors.CellError.from_row(row, note=note, field_name=k)
        return units_check
