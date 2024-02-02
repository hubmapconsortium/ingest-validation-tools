#!/usr/bin/env python3
import sys
from csv import DictWriter
import argparse

from ingest_validation_tools.schema_loader import (
    list_table_schema_versions,
    get_table_schema,
)


def main():
    default_fields = ["schema", "version", "field", "description", "enum"]
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--fields",
        default=default_fields,
        nargs="+",
        metavar="FIELD",
        help=f"Fields to include in report. Default: {default_fields}",
    )
    args = parser.parse_args()

    writer = DictWriter(sys.stdout, fieldnames=args.fields, extrasaction="ignore")
    writer.writeheader()

    for schema_version in list_table_schema_versions():
        schema = get_table_schema(schema_version)
        for field in schema["fields"]:
            if "constraints" in field and "enum" in field["constraints"]:
                enums = field["constraints"]["enum"]
            else:
                enums = [""]
            for enum in enums:
                writer.writerow(
                    {
                        "schema": schema_version.schema_name,
                        "version": schema_version.version,
                        "field": field["name"],
                        "description": field["description"],
                        "enum": enum,
                    }
                )
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
