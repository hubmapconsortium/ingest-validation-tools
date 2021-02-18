import csv

from frictionless import validate as validate_table


def get_table_errors(tsv_path, schema):
    pre_flight_errors = _get_pre_flight_errors(tsv_path, schema=schema)
    if pre_flight_errors:
        return pre_flight_errors

    report = validate_table(tsv_path, schema=schema,
                            format='csv')
    error_messages = report['errors']
    if 'tables' in report:
        for table in report['tables']:
            error_messages += [
                _get_message(error)
                for error in table['errors']
            ]
    return error_messages


def _get_pre_flight_errors(tsv_path, schema):
    dialect = csv.Sniffer().sniff(tsv_path.read_text())
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
                    errors.append(f'In column {i+1}, saw "{actual}", expected "{expected}"')
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
    if error['code'] == 'missing-label':
        raise Exception(f"Should have been caught pre-flight: {error['code']}")

    return (
        f'On row {error["rowPosition"]}, column "{error["fieldName"]}", '
        f'value "{error["cell"]}" fails because {error["note"]}'
    )


if __name__ == "__main__":
    import argparse
    from pathlib import Path
    from yaml import safe_load

    parser = argparse.ArgumentParser('CLI just for testing')
    parser.add_argument('--fixture', type=Path, required=True)
    args = parser.parse_args()
    tsv_path = args.fixture / 'input.tsv'
    schema_path = args.fixture / 'schema.yaml'
    errors = get_table_errors(tsv_path, safe_load(schema_path.read_text()))
    print('\n'.join(errors))
