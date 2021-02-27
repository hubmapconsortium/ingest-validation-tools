import csv
from pathlib import Path
import re

import frictionless
import requests


def get_table_errors(tsv, schema):
    tsv_path = Path(tsv)
    pre_flight_errors = _get_pre_flight_errors(tsv_path, schema=schema)
    if pre_flight_errors:
        return pre_flight_errors

    assert frictionless.__version__ == '4.0.0',\
        'Upgrade dependencies: "pip install -r requirements.txt"'

    url_check = _make_url_check(schema)
    sequence_limit_check = _make_sequence_limit_check(schema)
    units_check = _make_units_check(schema)

    report = frictionless.validate(tsv_path, schema=schema, format='csv', checks=[
                                   url_check, sequence_limit_check, units_check])

    assert len(report['errors']) == 0, f'report has errors: {report}'
    assert 'tasks' in report, f'"tasks" is missing: {report}'
    tasks = report['tasks']
    assert len(tasks) == 1, f'"tasks" not single: {report}'
    task = tasks[0]
    assert 'errors' in task, f'"tasks" missing "errors": {report}'

    return [
        _get_message(error)
        for error in task['errors']
    ]


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


def _make_url_check(schema):
    url_constrained_fields = _get_constrained_fields(schema, 'url')

    def url_check(row, schema=schema):
        for k, v in row.items():
            if k in url_constrained_fields:
                prefix = url_constrained_fields[k]['prefix']
                url = f'{prefix}{v}'
                status = _check_url_status_cache(url)
                if status != 200:
                    note = f'URL returned {status}: {url}'
                    yield frictionless.errors.CellError.from_row(row, note=note, field_name=k)
    return url_check


_prev_value_run_length = {}


def _make_sequence_limit_check(schema):
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


def _make_units_check(schema):
    units_constrained_fields = _get_constrained_fields(schema, 'units_for')

    def units_check(row, schema=schema):
        for k, v in row.items():
            if k in units_constrained_fields:
                units_for = units_constrained_fields[k]
                if (row[units_for] or row[units_for] == 0) and not row[k]:
                    note = f'Required when {units_for} is filled'
                    yield frictionless.errors.CellError.from_row(row, note=note, field_name=k)
    return units_check


def _get_pre_flight_errors(tsv_path, schema):
    try:
        dialect = csv.Sniffer().sniff(tsv_path.read_text())
    except csv.Error as e:
        return [str(e)]
    delimiter = dialect.delimiter
    expected_delimiter = '\t'
    if delimiter != expected_delimiter:
        return [f'Delimiter is {repr(delimiter)}, rather than expected {repr(expected_delimiter)}']

    # Re-reading the file is ugly, but creating a stream seems gratuitous.
    with tsv_path.open() as tsv_handle:
        reader = csv.DictReader(tsv_handle, dialect=dialect)
        fields = reader.fieldnames
        expected_fields = [f['name'] for f in schema['fields']]
        if fields != expected_fields:
            errors = []
            fields_set = set(fields)
            expected_fields_set = set(expected_fields)
            extra_fields = fields_set - expected_fields_set

            if extra_fields:
                errors.append(f'Unexpected fields: {extra_fields}')
            missing_fields = expected_fields_set - fields_set
            if missing_fields:
                errors.append(f'Missing fields: {missing_fields}')

            for i_pair in enumerate(zip(fields, expected_fields)):
                i, (actual, expected) = i_pair
                if actual != expected:
                    errors.append(f'In column {i+1}, found "{actual}", expected "{expected}"')
            return errors

    return None


def _get_message(error):
    '''
    >>> print(_get_message({
    ...     'cell': 'bad-id',
    ...     'fieldName': 'orcid_id',
    ...     'fieldNumber': 6,
    ...     'fieldPosition': 6,
    ...     'rowNumber': 1,
    ...     'rowPosition': 2,
    ...     'note': 'constraint "pattern" is "fake-re"',
    ...     'message': 'The message from the library is a bit confusing!',
    ...     'description': 'A field value does not conform to a constraint.'
    ... }))
    On row 2, column "orcid_id", value "bad-id" fails because constraint "pattern" is "fake-re"

    '''
    if 'code' in error and error['code'] == 'missing-label':
        return 'Bug: Should have been caught pre-flight. File an issue.'
    if 'rowPosition' in error and 'fieldName' in error and 'cell' in error and 'note' in error:
        return (
            f'On row {error["rowPosition"]}, column "{error["fieldName"]}", '
            f'value "{error["cell"]}" fails because {error["note"]}'
        )
    return error['message']


if __name__ == "__main__":
    import argparse
    from yaml import safe_load

    parser = argparse.ArgumentParser('CLI just for testing')
    parser.add_argument('--fixture', type=Path, required=True)
    args = parser.parse_args()
    tsv_path = args.fixture / 'input.tsv'
    schema_path = args.fixture / 'schema.yaml'
    errors = get_table_errors(tsv_path, safe_load(schema_path.read_text()))
    print('\n'.join(errors))
