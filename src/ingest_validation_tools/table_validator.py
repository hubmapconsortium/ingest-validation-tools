from frictionless import validate as validate_table


def get_table_errors(tsv_path, schema):
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

    return (
        f'On row {error["rowPosition"]}, column "{error["fieldName"]}", '
        f'value "{error["cell"]}" fails because {error["note"]}'
    )


if __name__ == "__main__":
    import argparse
    from pathlib import Path
    from yaml import safe_load

    parser = argparse.ArgumentParser('CLI just for testing')
    parser.add_argument('--tsv_path', type=Path, required=True)
    parser.add_argument('--schema_path', type=Path, required=True)
    args = parser.parse_args()
    errors = get_table_errors(args.tsv_path, safe_load(args.schema_path.read_text()))
    print('\n'.join(errors))
