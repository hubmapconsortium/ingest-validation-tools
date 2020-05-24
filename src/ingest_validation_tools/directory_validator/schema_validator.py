import os
from fnmatch import fnmatch

from jsonschema import Draft7Validator

from ingest_validation_tools.directory_validator.errors import \
    DirectoryValidationErrors


def validate(path, schema_dict, dataset_ignore_globs=[]):
    '''
    Given a directory path, and a JSON schema as a dict,
    validate the directory structure against the schema.
    '''
    Draft7Validator.check_schema(schema_dict)

    validator = Draft7Validator(schema_dict)
    as_list = [
        entry for entry in _dir_to_list(path, dataset_ignore_globs)
        if entry['name'] not in dataset_ignore_globs
    ]
    errors = list(validator.iter_errors(as_list))

    if errors:
        raise DirectoryValidationErrors(errors)


def _dir_to_list(path, dataset_ignore_globs):
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
            if any([
                fnmatch(entry.name, glob) for glob in dataset_ignore_globs
            ]):
                continue
            is_dir = entry.is_dir()
            item = {
                'type': 'directory' if is_dir else 'file',
                'name': entry.name
            }
            if is_dir:
                item['contents'] = _dir_to_list(
                    os.path.join(path, entry.name),
                    dataset_ignore_globs)
            items_to_return.append(item)
    return items_to_return
