from collections.abc import Iterator
from pathlib import Path
from typing import TypeVar

from ingest_validation_tools.schemas import DatasetSchema
from ingest_validation_tools.validation_utils import add_path

# KeyValuePair type hint is robust, but Validator is not available here; use generic
ValidatorGeneric = TypeVar("ValidatorGeneric")
KeyValuePair = Iterator[tuple[ValidatorGeneric, list[str | None]]]
PathOrStr = str | Path


class ValidatorError(Exception):
    pass


def run_plugin_validators_iter(
    metadata_path: PathOrStr,
    sv: DatasetSchema,
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

    returns: Iterator[Tuple[Validator, list[str | None]]]
         - Ran, no errors: (<ValidatorSubclassInstance>, [None])
         - Ran, errors: (<ValidatorSubclassNameInstance>, ["error"])
         - Did not run (not relevant to dataset_type): (<ValidatorSubclassInstance>, [])
    """

    if is_shared_upload:
        data_paths = [
            Path(metadata_path).parent / "global",
            Path(metadata_path).parent / "non_global",
        ]
    else:
        data_paths = sv.data_paths
    for k, v in validation_error_iter(
        data_paths,
        assay_type=sv.dataset_type,
        plugin_dir=plugin_dir,
        contains=sv.contains,
        verbose=verbose,
        schema_rows=sv.rows,
        globus_token=globus_token,
        app_context=app_context,
        **kwargs,
    ):
        yield k, v


def validation_error_iter(
    paths: list[Path],
    assay_type: str,
    plugin_dir: PathOrStr,
    contains: list,
    verbose: bool = False,
    schema_rows: list[dict] = [],
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
                paths,
                assay_type,
                contains,
                verbose,
                schema_rows,
                globus_token,
                app_context,
                **kwargs,
            )
            for err in validator.collect_errors():
                yield val_class, err
