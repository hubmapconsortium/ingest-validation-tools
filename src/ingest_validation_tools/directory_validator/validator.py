import os

from jsonschema import Draft7Validator

from ingest_validation_tools.directory_validator.errors import \
    DirectoryValidationErrors


def validate(path, schema_dict):
    '''
    Given a directory path, and a JSON schema as a dict,
    validate the directory structure against the schema.
    '''
    Draft7Validator.check_schema(schema_dict)

    validator = Draft7Validator(schema_dict)
    as_list = _dir_to_list(path)
    errors = list(validator.iter_errors(as_list))

    if errors:
        raise DirectoryValidationErrors(errors)


def _dir_to_list(path, ignore_dot_files=True):
    '''
    Walk the directory at `path`, and return a dict like that from `tree -J`:

    [
      {
        "type": "directory",
        "name": "some-directory",
        "contents": [
          { "type": "file", "name": "some-file.txt" }
        ]
      }
    ]
    '''

    items_to_return = []
    with os.scandir(path) as scan:
        for entry in sorted(scan, key=lambda entry: entry.name):
            if ignore_dot_files and entry.name[0] == '.':
                continue
            is_dir = entry.is_dir()
            item = {
                'type': 'directory' if is_dir else 'file',
                'name': entry.name
            }
            if is_dir:
                item['contents'] = _dir_to_list(os.path.join(path, entry.name))
            items_to_return.append(item)
    return items_to_return
