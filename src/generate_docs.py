#!/usr/bin/env python3

import argparse
import io
import json
import os
import re
import sys
import zipfile
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import quote, unquote

import requests
from tableschema_to_template.create_xlsx import create_xlsx
from yaml import dump as dump_yaml

from ingest_validation_tools.cli_utils import dir_path
from ingest_validation_tools.docs_utils import (
    generate_readme_md,
    generate_template_tsv,
    get_tsv_name,
    get_xlsx_name,
)
from ingest_validation_tools.schema_loader import (
    SchemaVersion,
    dict_directory_schema_versions,
    dict_table_schema_versions,
    enum_maps_to_lists,
    get_directory_schema,
    get_fields_wo_headers,
    get_pipeline_infos,
    get_table_schema,
)
from ingest_validation_tools.validation_utils import OtherTypes


def _simplify_dir_pattern(pattern: str) -> str:
    p = pattern.replace(r"\/", "/").replace(r"\.", ".")
    if p.endswith("/.*"):
        return p[:-2]
    p = p.replace("[^/]+", "*").replace("[^/]*", "*")
    p = re.sub(r"\(\?:([^)]+)\)", lambda m: "{" + m.group(1).replace("|", ",") + "}", p)
    return p


def _build_dir_tree(simplified_patterns: List[str]) -> dict:
    root: dict = {}
    for path in simplified_patterns:
        is_dir_node = path.endswith("/")
        parts = path.rstrip("/").split("/")
        node = root
        for i, part in enumerate(parts):
            is_last = i == len(parts) - 1
            if part not in node:
                node[part] = {"is_dir": not is_last or is_dir_node, "children": {}}
            elif not is_last or is_dir_node:
                node[part]["is_dir"] = True
            node = node[part]["children"]
    return root


def _render_dir_tree_node(name: str, node: dict, prefix: str, is_last: bool) -> List[str]:
    connector = "└── " if is_last else "├── "
    display = name + "/" if node["is_dir"] else name
    lines = [prefix + connector + display]
    child_prefix = prefix + ("    " if is_last else "│   ")
    children = list(node["children"].items())
    for i, (child_name, child_node) in enumerate(children):
        lines.extend(
            _render_dir_tree_node(child_name, child_node, child_prefix, i == len(children) - 1)
        )
    return lines


def _render_dir_tree(tree: dict) -> str:
    lines = ["."]
    items = list(tree.items())
    for i, (name, node) in enumerate(items):
        lines.extend(_render_dir_tree_node(name, node, "", i == len(items) - 1))
    return "\n".join(lines)


def _generate_directory_md(schema_name: str, directory_schema: dict) -> str:
    title = schema_name.replace("-", " ").title()
    files = directory_schema["files"]

    table_rows = ["| Pattern | Required? | Description |", "|--|--|--|"]
    for f in files:
        pattern = _simplify_dir_pattern(f["pattern"])
        required = "✓" if f.get("required", True) else ""
        qa_qc = "[QA/QC] " if f.get("is_qa_qc") else ""
        desc = qa_qc + f["description"]
        table_rows.append(f"| {pattern} | {required} | {desc} |")

    simplified = [_simplify_dir_pattern(f["pattern"]) for f in files]
    tree_text = _render_dir_tree(_build_dir_tree(simplified))
    yaml_text = dump_yaml(directory_schema, sort_keys=False)

    return (
        f"# {title}\n\n"
        "## File Hierarchy Schema\n\n"
        " This table details the file hierarchy schema specification.\n\n"
        + "\n".join(table_rows)
        + "\n\n\n## Directory Tree\n\n"
        "Here the file hierarchy schema is represented as a directory tree.\n\n"
        f"```\n{tree_text}\n```\n\n"
        "## YAML\n\n"
        "This is file hierarchy schema as YAML code that can be use with the HuBMAP "
        "[Ingest Validation Tools](https://github.com/hubmapconsortium/ingest-validation-tools)\n\n"
        f"```yaml\n{yaml_text}```\n"
    )


def _generate_empty_tree_zip(simplified_patterns: List[str]) -> bytes:
    buf = io.BytesIO()
    seen_dirs: set = set()

    def _add_dir(zf: zipfile.ZipFile, path: str) -> None:
        if path not in seen_dirs:
            zf.writestr(zipfile.ZipInfo(path), "")
            seen_dirs.add(path)

    def _ensure_parents(zf: zipfile.ZipFile, path: str) -> None:
        parts = path.rstrip("/").split("/")
        for j in range(1, len(parts)):
            _add_dir(zf, "/".join(parts[:j]) + "/")

    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in simplified_patterns:
            if path.endswith("/"):
                _ensure_parents(zf, path)
                _add_dir(zf, path)
            elif "*" not in path and "[" not in path and "(" not in path:
                _ensure_parents(zf, path)
                zf.writestr(path, "")
            elif "/" in path:
                parent = path.rsplit("/", 1)[0] + "/"
                _ensure_parents(zf, parent)
                _add_dir(zf, parent)

    return buf.getvalue()


def _fetch_bytes(url: str) -> Optional[bytes]:
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        return resp.content
    except Exception as e:
        print(f"Warning: could not fetch {url}: {e}", file=sys.stderr)
        return None


def _generate_doi_zip(
    schema_name: str,
    directory_schema: Optional[dict],
) -> bytes:
    buf = io.BytesIO()
    raw_base = "https://raw.githubusercontent.com/hubmapconsortium/dataset-metadata-spreadsheet/main"

    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for ext in ("tsv", "xlsx", "jsonld", "yml"):
            url = f"{raw_base}/{schema_name}/latest/{schema_name}.{ext}"
            content = _fetch_bytes(url)
            if content:
                zf.writestr(f"metadata.{ext}", content)

        if directory_schema:
            zf.writestr("directory.md", _generate_directory_md(schema_name, directory_schema))
            simplified = [_simplify_dir_pattern(f["pattern"]) for f in directory_schema["files"]]
            zf.writestr("empty_tree.zip", _generate_empty_tree_zip(simplified))

    return buf.getvalue()


def main():
    usage = """
        usage: generate_docs.py [-h] type target

        positional arguments:
        type        What type to generate
        target      Directory to write output to

        optional arguments:
        -h, --help  show this help message and exit
    """
    parser = argparse.ArgumentParser(usage=usage)
    parser.add_argument("type", help="What type to generate")
    parser.add_argument("target", type=dir_path, help="Directory to write output to")
    parser.add_argument("--cedar-api-key", help="CEDAR API key for fetching schema.json")
    args = parser.parse_args()

    if str(args.type).startswith("_"):
        return
    table_schema_versions = dict_table_schema_versions()[args.type]
    assert table_schema_versions, f"No versions for {args.type}"

    is_assay = args.type not in OtherTypes.with_sample_subtypes()
    table_schemas = {
        v.version: get_table_schema(v, keep_headers=True) for v in table_schema_versions
    }
    if is_assay:
        directory_schema_versions = sorted(dict_directory_schema_versions()[args.type])
        directory_schemas = {
            v: get_directory_schema(directory_type=args.type, version_number=v)
            for v in directory_schema_versions
        }
        pipeline_infos = get_pipeline_infos(args.type)
    else:
        directory_schemas = {}
        pipeline_infos = []

    # All the paths need to change.
    # We need to separate the docs into current and deprecated

    # Create deprecated and current directories
    deprecated_path = Path(args.target) / "deprecated"
    current_path = Path(args.target) / "current"

    if not deprecated_path.exists():
        os.mkdir(Path(args.target) / "deprecated")
    if not current_path.exists():
        os.mkdir(Path(args.target) / "current")

    # Separate docs into current and deprecated
    deprecated = {"metadata": {}, "directories": {}}
    current = {"metadata": {}, "directories": {}}

    for v, schema in table_schemas.items():
        if (
            not isinstance(schema["fields"][0], dict)
            or schema["fields"][0].get("name", "") != "is_cedar"
        ):
            deprecated["metadata"][v] = schema
        else:
            current["metadata"][v] = schema

    for v, schema in directory_schemas.items():
        try:
            assert float(v) >= 2.0
        except (AssertionError, ValueError):
            deprecated["directories"][v] = schema
        else:
            current["directories"][v] = schema

    # README can be placed in both places without any issue
    # README.md:
    if deprecated["metadata"]:
        with open(deprecated_path / "README.md", "w") as f:
            url = f"https://hubmapconsortium.github.io/ingest-validation-tools/{args.type}/"
            f.write(f"Moved to [github pages]({url}).")
    if current["metadata"]:
        with open(current_path / "README.md", "w") as f:
            url = f"https://hubmapconsortium.github.io/ingest-validation-tools/{args.type}/"
            f.write(f"Moved to [github pages]({url}).")

    # This is the actual content. We have to separate cedar and non-cedar schemas
    # CEDAR schemas go into current/index.md
    # Non-CEDAR schemas go into deprecated/index.md
    # index.md:
    if deprecated["metadata"]:
        with open(deprecated_path / "index.md", "w") as f:
            f.write(
                generate_readme_md(
                    table_schemas=deprecated["metadata"],
                    pipeline_infos=pipeline_infos,
                    directory_schemas=deprecated["directories"],
                    schema_name=args.type,
                    is_assay=is_assay,
                )
            )
    if current["metadata"]:
        with open(current_path / "index.md", "w") as f:
            f.write(
                generate_readme_md(
                    table_schemas=current["metadata"],
                    pipeline_infos=pipeline_infos,
                    directory_schemas=current["directories"],
                    schema_name=args.type,
                    is_assay=is_assay,
                )
            )

    # YAML:
    if deprecated["metadata"]:
        for v, schema in deprecated["metadata"].items():
            first_field = get_fields_wo_headers(schema)[0]
            if first_field["name"] == "version":
                expected = [v]
                actual = first_field["constraints"]["enum"]
                assert actual == expected, (
                    f"Wrong version constraint in {args.type}-v{v}.yaml; "
                    f"Expected {expected}; Actual {actual}"
                )

            # Need to determine how to check the is_cedar field.
            assert schema["fields"][0]

            if (
                not isinstance(schema["fields"][0], dict)
                or schema["fields"][0].get("name", "") != "is_cedar"
            ):
                # Just need to change the path here
                # since this is only relevant for non-CEDAR schemas
                with open(deprecated_path / f"v{v}.yaml", "w") as f:
                    f.write(
                        "# Generated YAML: PRs should not start here!\n"
                        + dump_yaml(schema, sort_keys=False)
                    )

        # Need to separate between CEDAR and non-CEDAR. Only run this for the non-CEDAR templates.

        # Data entry templates:
        max_version = max(deprecated["metadata"].keys())
        max_schema = enum_maps_to_lists(
            deprecated["metadata"][max_version],
            add_none_of_the_above=True,
            add_suggested=True,
        )
        max_schema["fields"] = get_fields_wo_headers(max_schema)
        if max_schema["fields"][0]["name"] != "is_cedar":
            with open(deprecated_path / get_tsv_name(args.type, is_assay=is_assay), "w") as f:
                f.write(generate_template_tsv(max_schema))
            create_xlsx(
                max_schema,
                deprecated_path / get_xlsx_name(args.type, is_assay=is_assay),
                idempotent=True,
                sheet_name="Export as TSV",
            )

    # DOI object zip for CEDAR schemas
    if current["directories"]:
        latest_dir_v = max(
            current["directories"].keys(),
            key=lambda v: tuple(int(x) for x in v.split(".")),
        )
        latest_dir_schema = current["directories"][latest_dir_v]
        doi_bytes = _generate_doi_zip(
            schema_name=args.type,
            directory_schema=latest_dir_schema,
        )
        with open(current_path / "doi-object.zip", "wb") as f:
            f.write(doi_bytes)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
