from typing import List, Union
from pathlib import Path


PathOrStr = Union[str, Path]


class ValidatorError(Exception):
    pass


class Validator(object):
    description = "This is a human-readable description"
    """str: human-readable description of the thing this validator validates
    """

    cost = 1.0
    """float: a rough measure of cost to run.  Lower is better.
    """

    def __init__(self, base_path: PathOrStr, assay_type: str):
        """
        base_path is expected to be a directory.
        This is the root path of the directory tree to be validated.
        assay_type is an assay type, one of a known set of strings.
        """
        self.path = (
            base_path
            if isinstance(base_path, Path)
            else Path(base_path)
        )
        if not self.path.is_dir():
            raise ValidatorError(f'{self.base_path} is not a directory')
        self.assay_type = assay_type

    def collect_errors(self) -> List[str]:
        """
        Returns a list of strings, each of which is a
        human-readable error message.

        "No error" is represented by returning an empty list.
        If the assay_type is not one for which this validator is intended,
        just return an empty list.
        """
        return []
