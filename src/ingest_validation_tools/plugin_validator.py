from collections.abc import Iterator
from pathlib import Path
from typing import Optional, TypeVar, Union

from ingest_validation_tools.schema_loader import SchemaVersion
from ingest_validation_tools.validation_utils import add_path

# KeyValuePair type hint is robust, but Validator is not available here; use generic
ValidatorGeneric = TypeVar("ValidatorGeneric")
KeyValuePair = Iterator[tuple[ValidatorGeneric, list[Union[str, None]]]]
PathOrStr = Union[str, Path]


class ValidatorError(Exception):
    pass


def run_plugin_validators_iter(
    metadata_path: PathOrStr,
    sv: SchemaVersion,
    plugin_dir: PathOrStr,
    is_shared_upload: bool,
    verbose: bool = True,
    globus_token: str = "",
    app_context: dict[str, str] = {},
    **kwargs,
) -> KeyValuePair:
    """
    Given a metadata.tsv file and a path to a directory of validator plugins, iterate through the
    results of applying each plugin to each row of the metadata.tsv file.  The 'assay_type' field
    of the metadata.tsv file is used to provide the assay, rather than the prefix of the filename.

    metadata_path: path to a metadata.tsv file
    plugin_dir: path to a directory containing validator classes

    returns: Iterator[Tuple[Validator, list[Union[str, None]]]]
         - Ran, no errors: (<ValidatorSubclassInstance>, [None])
         - Ran, errors: (<ValidatorSubclassNameInstance>, ["error"])
         - Did not run (not relevant to dataset_type): (<ValidatorSubclassInstance>, [])
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
            print(f"Data paths being passed to plugins: {data_paths}")
            for k, v in validation_error_iter(
                data_paths,
                sv.dataset_type,
                plugin_dir,
                sv.contains,
                verbose=verbose,
                schema=sv,
                globus_token=globus_token,
                app_context=app_context,
                **kwargs,
            ):
                yield k, v
        else:
            raise ValidatorError(f"{metadata_path} is missing values in 'data_path' column")


def validation_error_iter(
    paths: list[Path],
    assay_type: str,
    plugin_dir: PathOrStr,
    contains: list,
    verbose: bool = False,
    schema: Optional[SchemaVersion] = None,
    globus_token: str = "",
    app_context: dict[str, str] = {},
    **kwargs,
) -> KeyValuePair:
    """
    Given a list of base directories in the upload and a path to a directory
    of validator plugins, iterate over the results of applying all the plugin
    validators to each directory tree.

    paths: a list of paths representing the datasets in an upload
    assay_type: the assay type which produced the data in the directory tree
    plugin_dir: path to a directory containing validator classes
    contains: list of component assay types (empty if not multi-assay)

    returns an iterator the values of which are key value pairs representing
    error messages
    """
    with add_path(plugin_dir):
        try:
            from validator import validation_class_iter  # type: ignore

            print(f"Found plugins at {plugin_dir}")
        except Exception as e:
            raise ValidatorError(f"Could not import from plugin_dir {plugin_dir}: {e}")
        for val_class in validation_class_iter():
            validator = val_class(
                paths, assay_type, contains, verbose, schema, globus_token, app_context
            )
            kwargs["verbose"] = verbose
            for err in validator.collect_errors(**kwargs):
                yield val_class, err
