from importlib import import_module


def default_factory(base_path, assay_type):
    """
    default validator factory
    """
    return DefaultDirectoryContentValidator(base_path, assay_type)


DIRECTORY_CONTENT_VALIDATOR_FACTORY = default_factory


class DirectoryContentValidator(object):
    def __init__(self, base_path, assay_type):
        self.base_path = base_path
        self.assay_type = assay_type

    def collect_errors(self):
        """
        returns string or None.  Multiple errors are to be reported
        via a single multi-line string.
        """
        return None


class DefaultDirectoryContentValidator(DirectoryContentValidator):
    """
    Implements backward compatible calls to content validation modules
    """

    def collect_errors(self):
        validator = import_module(
            f'ingest_validation_tools.content_validation.{self.assay_type}')
        return validator.collect_errors(self.base_path)


class DirectoryContentValidationErrors(Exception):
    def __init__(self, errors):
        self.errors = errors


def validate_directory_content(assay_type, data_path):
    validator = DIRECTORY_CONTENT_VALIDATOR_FACTORY(data_path, assay_type)
    errors = validator.collect_errors()
    if errors:
        raise DirectoryContentValidationErrors(errors)
