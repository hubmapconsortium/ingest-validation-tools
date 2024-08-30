import inspect
import sys
from collections.abc import Iterator
from importlib import util
from pathlib import Path
from typing import List, Optional, Tuple, Type, Union

from ingest_validation_tools.schema_loader import SchemaVersion

PathOrStr = Union[str, Path]


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

    version = ""
    """string: in derived classes, a valid semantic version string.
    """

    def __init__(
        self,
        base_paths: List[Path],
        assay_type: str,
        contains: List = [],
        verbose: bool = False,
        **kwargs,
    ):
        """
        base_paths is expected to be a list of directories.
        These are the root paths of the directory trees to be validated.
        assay_type is an assay type, one of a known set of strings.
        """
        del kwargs
        if isinstance(base_paths, List):
            self.paths = [Path(path) for path in base_paths]
        elif isinstance(base_paths, Path):
            self.paths = [base_paths]
        elif isinstance(base_paths, str):
            self.paths = [Path(base_paths)]
        else:
            raise Exception(f"Validator init received base_paths arg as type {type(base_paths)}")
        self.assay_type = assay_type
        self.contains = contains
        self.verbose = verbose

    def _log(self, message):
        if self.verbose:
            print(message)
        return message

    def collect_errors(self, **kwargs) -> List[str]:
        """
        Returns a list of strings, each of which is a
        human-readable error message.

        "No error" is represented by returning an empty list.
        If the assay_type is not one for which this validator is intended,
        just return an empty list.
        """
        raise NotImplementedError()


KeyValuePair = Tuple[Type[Validator], Optional[str]]


def run_plugin_validators_iter(
    metadata_path: PathOrStr,
    sv: SchemaVersion,
    plugin_dir: PathOrStr,
    is_shared_upload: bool,
    verbose: bool = True,
    **kwargs,
) -> Iterator[KeyValuePair]:
    """
    Given a metadata.tsv file and a path to a directory of Validator plugins, iterate through the
    results of applying each plugin to each row of the metadata.tsv file.  The 'assay_type' field
    of the metadata.tsv file is used to provide the assay, rather than the prefix of the filename.

    metadata_path: path to a metadata.tsv file
    plugin_dir: path to a directory containing classes derived from Validator

    returns an iterator the values of which are key value pairs representing error messages.
    """

    for column_name in ["assay_type", "dataset_type"]:
        if column_name in sv.rows[0]:
            if any(row[column_name] != sv.dataset_type for row in sv.rows):
                raise ValidatorError(f"{metadata_path} contains more than one assay type")

    data_paths = []
    if is_shared_upload:
        paths = [Path(metadata_path).parent / "global", Path(metadata_path).parent / "non_global"]
        for k, v in validation_error_iter(
            paths, sv.dataset_type, plugin_dir, sv.contains, **kwargs
        ):
            yield k, v
    else:
        if all("data_path" in row for row in sv.rows):
            for row in sv.rows:
                data_path = Path(row["data_path"])
                if not data_path.is_absolute():
                    data_path = Path(metadata_path).parent / data_path
                if not data_path.is_dir():
                    raise ValidatorError(f"{data_path} should be the base directory of a dataset")
                data_paths.append(data_path)
            for k, v in validation_error_iter(
                data_paths, sv.dataset_type, plugin_dir, sv.contains, verbose=verbose, **kwargs
            ):
                yield k, v
        else:
            raise ValidatorError(f"{metadata_path} is missing values in 'data_path' column")


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
                if inspect.isclass(obj) and obj != Validator and issubclass(obj, Validator):
                    sort_me.append((obj.cost, obj.description, obj))
    sort_me.sort()
    for _, _, cls in sort_me:
        yield cls


def validation_error_iter(
    paths: List[Path],
    assay_type: str,
    plugin_dir: PathOrStr,
    contains: List,
    verbose: bool = False,
    **kwargs,
) -> Iterator[KeyValuePair]:
    """
    Given a list of base directories in the upload and a path to a directory
    of Validator plugins, iterate over the results of applying all the plugin
    validators to each directory tree.

    paths: a list of paths representing the datasets in an upload
    assay_type: the assay type which produced the data in the directory tree
    plugin_dir: path to a directory containing classes derived from Validator
    contains: list of component assay types (empty if not multi-assay)

    returns an iterator the values of which are key value pairs representing
    error messages
    """
    for cls in validation_class_iter(plugin_dir):
        validator = cls(paths, assay_type, contains, verbose)
        kwargs["verbose"] = verbose
        for err in validator.collect_errors(**kwargs):
            yield cls, err
