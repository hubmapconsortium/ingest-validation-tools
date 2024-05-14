#!/usr/bin/env python3

import argparse
import os
import sys
from pathlib import Path

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
    dict_directory_schema_versions,
    dict_table_schema_versions,
    enum_maps_to_lists,
    get_directory_schema,
    get_fields_wo_headers,
    get_pipeline_infos,
    get_table_schema,
)
from ingest_validation_tools.validation_utils import OtherTypes


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("type", help="What type to generate")
    parser.add_argument("target", type=dir_path, help="Directory to write output to")
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


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
