import re

import frictionless
import requests


def _get_constrained_fields(schema, constraint):
    c_c = 'custom_constraints'
    return {
        f['name']: f[c_c][constraint] for f in schema['fields']
        if c_c in f and constraint in f[c_c]
    }


_url_status_cache = {}


def _check_url_status_cache(url):
    if url not in _url_status_cache:
        response = requests.get(url)
        _url_status_cache[url] = response.status_code
    return _url_status_cache[url]


def make_url_check(schema):
    url_constrained_fields = _get_constrained_fields(schema, 'url')

    def url_check(row, schema=schema):
        for k, v in row.items():
            if v is None:
                continue
            if k in url_constrained_fields:
                prefix = url_constrained_fields[k]['prefix']
                url = f'{prefix}{v}'
                status = _check_url_status_cache(url)
                if status != 200:
                    note = f'URL returned {status}: {url}'
                    yield frictionless.errors.CellError.from_row(row, note=note, field_name=k)
    return url_check


_prev_value_run_length = {}


def make_sequence_limit_check(schema):
    sequence_limit_fields = _get_constrained_fields(schema, 'sequence_limit')

    def sequence_limit_check(row, schema=schema):
        prefix_number_re = r'(?P<prefix>.*?)(?P<number>\d+)$'
        for k, v in row.items():
            if k not in sequence_limit_fields or not v:
                continue

            match = re.search(prefix_number_re, v)
            if not match:
                del _prev_value_run_length[k]
                continue

            if k not in _prev_value_run_length:
                _prev_value_run_length[k] = (v, 1)
                continue

            prev_value, run_length = _prev_value_run_length[k]
            prev_match = re.search(prefix_number_re, prev_value)
            if (
                match.group('prefix') != prev_match.group('prefix') or
                int(match.group('number')) != int(prev_match.group('number')) + 1
            ):
                _prev_value_run_length[k] = (v, 1)
                continue

            run_length += 1
            _prev_value_run_length[k] = (v, run_length)

            limit = sequence_limit_fields[k]
            if run_length >= limit:
                note = f'incremented {run_length} times; limit is {limit}'
                yield frictionless.errors.CellError.from_row(row, note=note, field_name=k)

    return sequence_limit_check


def make_units_check(schema):
    units_constrained_fields = _get_constrained_fields(schema, 'units_for')

    def units_check(row, schema=schema):
        for k, v in row.items():
            if k in units_constrained_fields:
                units_for = units_constrained_fields[k]
                if (row[units_for] or row[units_for] == 0) and not row[k]:
                    note = f'Required when {units_for} is filled'
                    yield frictionless.errors.CellError.from_row(row, note=note, field_name=k)
    return units_check
