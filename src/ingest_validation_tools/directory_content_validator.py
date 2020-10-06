from os import walk
from pathlib import Path


def _directory_validator_factory(base_path, assay_type):
    # TODO: Create other Validator subclasses, and return them instead,
    # depending on assay_type.
    return DirectoryContentValidator(base_path, assay_type)


def _get_file_start_error(file_path):
    suffix = file_path.suffix
    if suffix == '.gz':
        with file_path.open('rb') as f:
            bytes = f.read(2)
            expected = b'\x1F\x8B'
            if bytes != expected:
                return f'Unexpected bytes ({bytes}) at start of .gz file'
    return None


class DirectoryContentValidator(object):
    def __init__(self, base_path, assay_type):
        self.base_path = base_path
        self.assay_type = assay_type

    def collect_file_errors(self):
        errors = {}
        for root, _dirs, files in walk(self.base_path):
            for f in files:
                file_path = Path(root) / f
                start_error = _get_file_start_error(file_path)
                if start_error:
                    errors[str(file_path)] = start_error
        return errors

    def collect_other_errors(self):
        return {}

    def collect_errors(self):
        errors = {}
        file_errors = self.collect_file_errors()
        if file_errors:
            errors['File content'] = file_errors

        other_errors = self.collect_other_errors()
        if other_errors:
            errors['Other'] = other_errors

        return errors


class DirectoryContentValidationErrors(Exception):
    def __init__(self, errors):
        self.errors = errors


def validate_directory_content(assay_type, data_path):
    validator = _directory_validator_factory(data_path, assay_type)
    errors = validator.collect_errors()
    if errors:
        raise DirectoryContentValidationErrors(errors)
