import sys
from importlib import util
import inspect
from typing import List, Union, Tuple, Iterator, Type
from pathlib import Path
from csv import Error as CsvError

from ingest_validation_tools.validation_utils import (
    dict_reader_wrapper,
    get_context_of_decode_error,
)

PathOrStr = Union[str, Path]

KeyValuePair = Tuple[str, str]


class add_path:
    """
    Add an element to sys.path using a context.
    Thanks to Eugene Yarmash https://stackoverflow.com/a/39855753
    """

    def __init__(self, path):
        self.path = path

    def __enter__(self):
        sys.path.insert(0, self.path)

    def __exit__(self, exc_type, exc_value, traceback):
        del exc_type, exc_value, traceback
        try:
            sys.path.remove(self.path)
        except ValueError:
            pass


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
            raise ValidatorError(f"{self.path} is not a directory")
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


def run_plugin_validators_iter(
    metadata_path: PathOrStr, plugin_dir: PathOrStr, **kwargs
) -> Iterator[KeyValuePair]:
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
            rows = dict_reader_wrapper(metadata_path, "ascii")
            # TODO: Pass in encoding.
            # https://github.com/hubmapconsortium/ingest-validation-tools/issues/494
        except (CsvError, IOError):
            raise ValidatorError(f"{metadata_path} could not be parsed as a .tsv file")
        except UnicodeDecodeError as e:
            raise ValidatorError(get_context_of_decode_error(e))
        if not rows:
            raise ValidatorError(f"{metadata_path} has no data rows")
        if all("assay_type" in row for row in rows):
            assay_type = rows[0]["assay_type"]
            if any(row["assay_type"] != assay_type for row in rows):
                raise ValidatorError(
                    f"{metadata_path} contains more than one assay type"
                )
        elif all("dataset_type" in row for row in rows):
            assay_type = rows[0]["dataset_type"]
            if any(row["dataset_type"] != assay_type for row in rows):
                raise ValidatorError(
                    f"{metadata_path} contains more than one dataset type"
                )

        else:
            raise ValidatorError(f'{metadata_path} has no "assay_type" column')
    else:
        raise ValidatorError(f"{metadata_path} does not exist or is not a file")

    if all("data_path" in row for row in rows):
        for row in rows:
            data_path = Path(row["data_path"])
            if not data_path.is_absolute():
                data_path = (metadata_path.parent / data_path).resolve()
            for k, v in validation_error_iter(
                data_path, assay_type, plugin_dir, **kwargs
            ):
                yield k, v
    else:
        raise ValidatorError(f'{metadata_path} has no "data_path" column')


def validation_class_iter(plugin_dir: PathOrStr) -> Iterator[Type[Validator]]:
    """
    Given a directory of Validator plugins, return the validator types
    in order of increasing cost.

    plugin_dir: path to a directory containing classes derived from Validator
    """
    plugin_dir = Path(plugin_dir)
    plugins = list(plugin_dir.glob("*.py"))
    if not plugins:
        raise ValidatorError(f"{plugin_dir}/*.py does not match any validation plugins")
    sort_me = []
    with add_path(str(plugin_dir)):
        for fpath in plugin_dir.glob("*.py"):
            mod_nm = fpath.stem
            if mod_nm in sys.modules:
                mod = sys.modules[mod_nm]
            else:
                spec = util.spec_from_file_location(mod_nm, fpath)
                if spec is None:
                    raise ValidatorError(f"bad plugin test {fpath}")
                mod = util.module_from_spec(spec)
                sys.modules[mod_nm] = mod
                spec.loader.exec_module(mod)  # type: ignore
            for _, obj in inspect.getmembers(mod):
                if (
                    inspect.isclass(obj)
                    and obj != Validator
                    and issubclass(obj, Validator)
                ):
                    sort_me.append((obj.cost, obj.description, obj))
    sort_me.sort()
    for _, _, cls in sort_me:
        yield cls


def validation_error_iter(
    base_dir: PathOrStr, assay_type: str, plugin_dir: PathOrStr, **kwargs
) -> Iterator[KeyValuePair]:
    """
    Given a base directory pointing to a tree of upload data files and a
    path to a directory of Validator plugins, iterate over the results of
    applying all the plugin validators to the directory tree.

    base_dir: the root of a directory tree of upload data files
    assay_type: the assay type which produced the data in the directory tree
    plugin_dir: path to a directory containing classes derived from Validator

    returns an iterator the values of which are key value pairs representing
    error messages
    """
    base_dir = Path(base_dir)
    if not base_dir.is_dir():
        raise ValidatorError(f"{base_dir} should be the base directory of a dataset")
    for cls in validation_class_iter(plugin_dir):
        validator = cls(base_dir, assay_type)
        for err in validator.collect_errors(**kwargs):  # type: ignore
            yield cls.description, err
