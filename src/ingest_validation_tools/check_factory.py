import re
from string import Template
from pathlib import Path
from sys import stderr
import json

import frictionless
import requests


cache_path = Path(__file__).parent / 'url-status-cache.json'


def make_checks(schema):
    factory = _CheckFactory(schema)
    return [
        factory.make_url_check(),
        factory.make_sequence_limit_check(),
        factory.make_units_check(),
        factory.make_forbid_na_check()
    ]


class _CheckFactory():
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
        if not cache_path.exists():
            cache_path.write_text('{}')
        url_status_cache = json.loads(cache_path.read_text())
        if url not in url_status_cache:
            print(f'Fetching un-cached url: {url}', file=stderr)
            try:
                response = requests.get(url, verify=False)
                url_status_cache[url] = response.status_code
            except Exception as e:
                url_status_cache[url] = str(e)
            cache_path.write_text(json.dumps(
                url_status_cache,
                sort_keys=True,
                indent=2
            ))
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

    def make_forbid_na_check(self, template=Template(
            '"N/A" fields should just be left empty')):
        forbid_na_constrained_fields = self._get_constrained_fields('forbid_na')

        def forbid_na_check(row):
            for k, v in row.items():
                if (
                    k in forbid_na_constrained_fields
                    and isinstance(v, str)
                    and v.upper() in ['NA', 'N/A']
                ):
                    note = template.substitute()
                    yield frictionless.errors.CellError.from_row(row, note=note, field_name=k)
        return forbid_na_check
