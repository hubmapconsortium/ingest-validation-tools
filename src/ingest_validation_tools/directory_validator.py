import os
import re
from fnmatch import fnmatch
from typing import List, Dict, Tuple
from pathlib import Path
from ingest_validation_tools.yaml_include_loader import load_yaml


class DirectoryValidationErrors(Exception):
    def __init__(self, errors):
        self.errors = errors


def validate_directory(
    path: Path, schema_files: List[Dict], dataset_ignore_globs: List[str] = []
) -> None:
    """
    Given a directory path, and a directory schema,
    raise DirectoryValidationErrors if there are errors.
    """
    try:
        required_patterns, allowed_patterns = _get_required_allowed(schema_files)
        dependencies = _get_dependencies(schema_files)
    except KeyError as e:
        raise DirectoryValidationErrors(f"Error finding patterns for {path}: {e}")
    required_missing_errors: List[str] = []
    not_allowed_errors: List[str] = []
    if not path.exists():
        # TODO: this seems more like the content of the TSV errors section
        raise FileNotFoundError(0, "No such file or directory", str(path))
    actual_paths = []
    for triple in os.walk(path):
        (dir_path, _, file_names) = triple
        # [1:] removes leading '/', if any.
        prefix = dir_path.replace(str(path), "")[1:]
        if os.name == "nt":
            # Convert MS backslashes to forward slashes.
            prefix = prefix.replace("\\", "/")
        actual_paths += (
            [f"{prefix}/{name}" for name in file_names] if prefix else file_names
        )

    """TODO: message_munger adds periods at the end of these messages
    which is very confusing for regex! Also human readability of required_patterns
    is extremely poor.
    """

    # Iterate over the conditional paths and pop them from the actual_paths list
    for dependency in dependencies:
        dependency_pattern = dependency.get("pattern")
        assert isinstance(dependency_pattern, str)
        # Check to see whether there's a match
        matching_paths = [
            actual
            for actual in actual_paths
            if re.fullmatch(dependency_pattern, actual)
        ]
        # If there's a match, then we have to check that the dependent items are also captured
        # Let's also short-circuit and get failures out of the way
        if dependency.get("required") and not matching_paths:
            required_missing_errors.append(dependency_pattern)
            continue

        dependency_items = dependency.get("dependency", {}).get("files")

        (
            dependency_required_patterns,
            dependency_allowed_patterns,
        ) = _get_required_allowed(dependency_items)

        # We should iterate over the matching_paths first and make sure they're all allowed
        not_allowed_errors.extend(
            _get_not_allowed_errors(
                matching_paths, dependency_allowed_patterns, dataset_ignore_globs
            )
        )
        required_missing_errors.extend(
            _get_missing_required_errors(matching_paths, dependency_required_patterns)
        )

        actual_paths = list(set(actual_paths) - set(matching_paths))

    not_allowed_errors.extend(
        _get_not_allowed_errors(actual_paths, allowed_patterns, dataset_ignore_globs)
    )
    required_missing_errors.extend(
        _get_missing_required_errors(actual_paths, required_patterns)
    )

    errors = {}
    if not_allowed_errors:
        errors["Not allowed"] = sorted(not_allowed_errors)
    if required_missing_errors:
        errors["Required but missing"] = sorted(required_missing_errors)
    if errors:
        raise DirectoryValidationErrors(errors)


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


def _get_missing_required_errors(
    paths: List[str], required_patterns: List[str]
) -> List[str]:
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
    allowed = [item["pattern"] for item in dir_schema if "dependency" not in item]
    required = [
        item["pattern"]
        for item in dir_schema
        if ("required" not in item or item["required"]) and "dependency" not in item
    ]
    return required, allowed


def _get_dependencies(dir_schema: List[Dict]) -> List[Dict]:
    dependencies = []
    for item in dir_schema:
        item_dependency = item.get("dependency")
        if item_dependency:
            # Try to load the dependency.
            dependency_path = (
                Path(__file__).parent
                / "directory-schemas/dependencies"
                / f"{item_dependency}.yaml"
            )
            dependency = load_yaml(dependency_path)
            item.update({"dependency": dependency})
            dependencies.append(item)

    return dependencies
