import os
import re
from fnmatch import fnmatch
from pathlib import Path
from typing import Dict, List, Tuple


class DirectoryValidationErrors(Exception):
    def __init__(self, errors):
        self.errors = errors


def validate_directory(
    paths: list[Path], schema_files: List[Dict], dataset_ignore_globs: List[str] = []
) -> None:
    """
    Given a list of directory paths, and a directory schema,
    raise DirectoryValidationErrors if there are errors.
    """
    try:
        required_patterns, allowed_patterns = _get_required_allowed(schema_files)
    except KeyError as e:
        raise DirectoryValidationErrors(
            f"Error finding patterns" f" for {','.join([x.as_posix() for x in paths])}: {e}"
        )
    required_missing_errors: List[str] = []
    not_allowed_errors: List[str] = []
    actual_paths = get_files(paths)
    not_allowed_errors.extend(
        _get_not_allowed_errors(actual_paths, allowed_patterns, dataset_ignore_globs)
    )
    required_missing_errors.extend(_get_missing_required_errors(actual_paths, required_patterns))

    errors = {}
    if not_allowed_errors:
        errors["Not allowed"] = sorted(not_allowed_errors)
    if required_missing_errors:
        errors["Required but missing"] = sorted(required_missing_errors)
    if errors:
        raise DirectoryValidationErrors(errors)


def get_files(paths: list[Path]) -> list[str]:
    actual_paths = []
    for path in paths:
        if not path.exists():
            raise FileNotFoundError(0, "No such file or directory", str(path))

        for triple in os.walk(path):
            (dir_path, _, file_names) = triple
            # [1:] removes leading '/', if any.
            prefix = dir_path.replace(str(path), "")[1:]
            if os.name == "nt":
                # Convert MS backslashes to forward slashes.
                prefix = prefix.replace("\\", "/")
            # If this is not the root of the path and is a leaf directory
            if not file_names and prefix:
                actual_paths += [f"{prefix}/"]
            # Otherwise this should be a branch directory
            else:
                actual_paths += (
                    [f"{prefix}/{name}" for name in file_names] if prefix else file_names
                )
    return actual_paths


def _get_not_allowed_errors(
    paths: List[str], allowed_patterns: List[str], ignore_globs: List[str]
) -> List[str]:
    not_allowed_errors = []
    for path in paths:
        if any(fnmatch(path, glob) for glob in ignore_globs):
            continue
        if not any(re.fullmatch(pattern, path) for pattern in allowed_patterns):
            not_allowed_errors.append(path)

    return not_allowed_errors


def _get_missing_required_errors(paths: List[str], required_patterns: List[str]) -> List[str]:
    return [
        pattern
        for pattern in required_patterns
        if not any(re.fullmatch(pattern, path) for path in paths)
    ]


def _get_required_allowed(dir_schema: List[Dict]) -> Tuple[List[str], List[str]]:
    """
    Given a directory_schema, return a pair of regex lists:
    Those regexes which are required, and those which are allowed.

    >>> schema = [
    ...    {'pattern': 'this_is_required'},
    ...    {'pattern': 'this_is_optional', 'required': False}
    ... ]
    >>> _get_required_allowed(schema)
    (['this_is_required'], ['this_is_required', 'this_is_optional'])

    """
    allowed = [item["pattern"] for item in dir_schema]
    required = [
        item["pattern"] for item in dir_schema if ("required" not in item or item["required"])
    ]
    return required, allowed
