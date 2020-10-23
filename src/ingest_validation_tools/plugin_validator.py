import sys
import importlib
import inspect
from typing import List, Union, Tuple, Iterator
from pathlib import Path
from csv import DictReader

PathOrStr = Union[str, Path]

KeyValuePair = Tuple[str, str]


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
        self.path = Path(base_path)
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
        raise NotImplementedError()


def run_plugin_validators_iter(metadata_path: PathOrStr,
                               plugin_dir: PathOrStr) -> Iterator[KeyValuePair]:
    """
    Given a metadata.tsv file and a path to a directory of Validator plugins, iterate through the
    results of applying each plugin to each row of the metadata.tsv file.  The 'assay_type' field
    of the metadata.tsv file is used to provide the assay, rather than the prefix of the filename.

    metadata_path: path to a metadata.tsv file
    plugin_dir: path to a directory containing classes derived from Validator

    returns an iterator the values of which are key value pairs representing error messages.
    """
    metadata_path = Path(metadata_path)
    if metadata_path.is_file():
        try:
            with open(metadata_path, encoding='latin-1') as f:
                rows = list(DictReader(f, dialect='excel-tab'))
        except Exception:
            raise ValidatorError(f'{metadata_path} could not be parsed as a .tsv file')
        if not rows:
            raise ValidatorError(f'{metadata_path} has no data rows')
        if all('assay_type' in row for row in rows):
            assay_type = rows[0]['assay_type']
            if any(row['assay_type'] != assay_type for row in rows):
                raise ValidatorError(f'{metadata_path} contains more than one assay type')

        else:
            raise ValidatorError(f'{metadata_path} has no "assay_type" column')
    else:
        raise ValidatorError(f'{metadata_path} does not exist or is not a file')

    if all('data_path' in row for row in rows):
        for row in rows:
            data_path = Path(row['data_path'])
            if not data_path.is_absolute():
                data_path = (metadata_path / data_path).resolve()
            for k, v in validation_error_iter(data_path, assay_type, plugin_dir):
                yield k, v
    else:
        raise ValidatorError(f'{metadata_path} has no "data_path" column')


def validation_error_iter(base_dir: PathOrStr, assay_type: str,
                          plugin_dir: PathOrStr) -> Iterator[KeyValuePair]:
    """
    Given a base directory pointing to a tree of submission data files and a
    path to a directory of Validator plugins, iterate over the results of
    applying all the plugin validators to the directory tree.

    base_dir: the root of a directory tree of submission data files
    assay_type: the assay type which produced the data in the directory tree
    plugin_dir: path to a directory containing classes derived from Validator

    returns an iterator the values of which are key value pairs representing
    error messages
    """
    base_dir = Path(base_dir)
    plugin_dir = Path(plugin_dir)
    if not base_dir.is_dir():
        raise ValidatorError(f'{base_dir} should be the base directory of a dataset')
    if not plugin_dir.is_dir():
        raise ValidatorError(f'{plugin_dir} should be a directory of validation plug-ins')
    for fpath in plugin_dir.glob('*.py'):
        mod_nm = fpath.stem
        if mod_nm in sys.modules:
            mod = sys.modules[mod_nm]
        else:
            spec = importlib.util.spec_from_file_location(mod_nm, fpath)
            mod = importlib.util.module_from_spec(spec)
            sys.modules[mod_nm] = mod
            spec.loader.exec_module(mod)
        sort_me = []
        for name, obj in inspect.getmembers(mod):
            if inspect.isclass(obj) and obj != Validator and issubclass(obj, Validator):
                sort_me.append((obj.cost, obj.description, obj))
        sort_me.sort()
        for cost, description, cls in sort_me:
            validator = cls(base_dir, assay_type)
            for err in validator.collect_errors():
                yield description, err
