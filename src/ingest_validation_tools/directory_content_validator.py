def _validator_factory(base_path, assay_type):
    # TODO: Create other Validator subclasses, and return them instead,
    # depending on assay_type.
    return DirectoryContentValidator(base_path, assay_type)


class DirectoryContentValidator(object):
    def __init__(self, base_path, assay_type):
        self.base_path = base_path
        self.assay_type = assay_type

    def collect_errors(self):
        """
        Subclasses should return an array listing the errors,
        or if more structure is desired, a dict.
        """
        return []


class DirectoryContentValidationErrors(Exception):
    def __init__(self, errors):
        self.errors = errors


def validate_directory_content(assay_type, data_path):
    validator = _validator_factory(data_path, assay_type)
    errors = validator.collect_errors()
    if errors:
        raise DirectoryContentValidationErrors(errors)
