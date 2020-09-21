from pathlib import Path

from yaml import safe_load as load_yaml


_table_schemas_path = Path(__file__).parent / 'table-schemas'
_directory_schemas_path = Path(__file__).parent / 'directory-schemas'


def list_types():
    schemas = {
        p.stem for p in
        (_table_schemas_path / 'level-2').iterdir()
    }
    return sorted(schemas)


def get_sample_schema():
    return load_yaml(
        (Path(__file__).parent / 'table-schemas' / 'sample.yaml').read_text()
    )


def get_directory_schemas(type):
    single_path = _directory_schemas_path / f'{type}.yaml'
    all_paths = (
        [single_path] if single_path.exists()
        else _directory_schemas_path.glob(f'{type}-*.yaml')
    )
    return {
        path.stem: load_yaml(open(path).read())
        for path in all_paths
    }


def get_table_schema(type, optional_fields=[]):
    table_type = type.split('-')[0]

    level_1_fields = _get_level_1_schema('level-1')['fields']
    paths_fields = _get_level_1_schema('paths')['fields']
    type_schema = _get_level_2_schema(table_type)
    type_fields = type_schema['fields']

    (level_1_fields_plus_overrides, type_fields_minus_overrides) = \
        _apply_overrides(level_1_fields, type_fields)

    fields = (
        level_1_fields_plus_overrides
        + type_fields_minus_overrides
        + paths_fields
    )
    for field in fields:
        _add_constraints(field, optional_fields)
    for field in fields:
        _validate_field(field)
    return {
        'doc_url': type_schema['doc_url'],
        'fields': fields
    }


def _validate_field(field):
    if field['name'].endswith('_unit') and 'enum' not in field['constraints']:
        raise Exception('"_unit" fields must have enum constraints', field)


def _get_level_1_schema(type):
    return load_yaml(open(_table_schemas_path / f'{type}.yaml').read())


def _get_level_2_schema(type):
    return load_yaml(open(
        _table_schemas_path / 'level-2' / f'{type}.yaml'
    ).read())


def _apply_overrides(high_fields, low_fields):
    '''
    Given two lists of fields, find fields with the same names in both,
    and add the defintions from low_fields to high_fields,
    and return the new modified high_fields, and low_fields,
    without the fields which were there just to override.

    >>> a, b = _apply_overrides(
    ...  [{'name': 'A', 'type': '???'}],
    ...  [{'name': 'A', 'type': '!!!'}, {'name': 'B'}]
    ... )

    >>> a
    [{'name': 'A', 'type': '!!!'}]

    >>> b
    [{'name': 'B'}]

    '''
    high_field_names = {field['name'] for field in high_fields}
    low_field_names = {field['name'] for field in low_fields}
    override_field_names = set.intersection(
        high_field_names, low_field_names)

    override_fields_dict = {
        name: [f for f in low_fields if f['name'] == name][0]
        for name in override_field_names
    }

    _check_enum_consistency(high_fields, override_fields_dict)

    high_fields_plus_overrides = [
        (
            # TODO: Python 3.9 will add "|" for dict merging.
            {**field, **override_fields_dict[field['name']]}
            if field['name'] in override_field_names
            else field
        )
        for field in high_fields
    ]
    low_fields_minus_overrides = [
        field for field in low_fields
        if field['name'] not in override_field_names
    ]
    return high_fields_plus_overrides, low_fields_minus_overrides


def _check_enum_consistency(high_fields, override_fields_dict):
    '''
    >>> high_fields = [{
    ...    'name': 'vowels',
    ...    'constraints': {'enum': ['a', 'e', 'i', 'o', 'u']}
    ... }]
    >>> override_fields_dict = {'vowels': {
    ...    'constraints': {'enum': ['a', 'b', 'c']}
    ... }}
    >>> try:
    ...   _check_enum_consistency(high_fields, override_fields_dict)
    ... except Exception as e:
    ...   a = str(e).split('; ')
    ...   print(a[0])
    ...   print(a[1])
    In vowels, surprised by: ['b', 'c']
    Should be one of ['a', 'e', 'i', 'o', 'u']

    '''
    high_field_constraints = {
        field['name']: field['constraints'] for field in high_fields
        if 'constraints' in field
    }
    for field_name, override in override_fields_dict.items():
        if (
            'constraints' in override
            and 'enum' in override['constraints']
        ):
            override_enum = set(override['constraints']['enum'])
            high_field_enum = set(high_field_constraints[field_name]['enum'])
            if not (override_enum < high_field_enum):
                surprise = override_enum - high_field_enum
                raise Exception(
                    f'In {field_name}, surprised by: {sorted(surprise)}; '
                    f'Should be one of {sorted(high_field_enum)}')


def _add_constraints(field, optional_fields):
    '''
    Modifies field in-place, adding implicit constraints
    based on the field name.

    >>> from pprint import pprint
    >>> field = {'name': 'abc_percent'}
    >>> _add_constraints(field, [])
    >>> pprint(field, width=40)
    {'constraints': {'maximum': 100,
                     'minimum': 0,
                     'required': True},
     'name': 'abc_percent',
     'type': 'number'}

    >>> field = {'name': 'optional_value'}
    >>> _add_constraints(field, ['optional_value'])
    >>> pprint(field, width=40)
    {'constraints': {'required': False},
     'name': 'optional_value',
     'type': 'number'}

    '''
    if 'constraints' not in field:
        field['constraints'] = {}

    # Guess constraints:
    if 'required' not in field['constraints']:
        field['constraints']['required'] = True
    if 'protocols_io_doi' in field['name']:
        field['constraints']['pattern'] = r'10\.17504/.*'
    if field['name'].endswith('_email'):
        field['format'] = 'email'

    # Guess types:
    if field['name'].startswith('is_'):
        field['type'] = 'boolean'
    if field['name'].endswith('_value'):
        field['type'] = 'number'
    if field['name'].startswith('number_of_'):
        field['type'] = 'integer'
    if 'percent' in field['name']:
        field['type'] = 'number'
        field['constraints']['minimum'] = 0
        field['constraints']['maximum'] = 100

    # Override:
    if field['name'] in optional_fields:
        field['constraints']['required'] = False
