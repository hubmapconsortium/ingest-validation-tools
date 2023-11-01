import csv
from pathlib import Path
from typing import List, Optional, Dict, Union
from enum import Enum

import frictionless

from ingest_validation_tools.check_factory import make_checks


class ReportType(Enum):
    STR = 1
    JSON = 2


def get_table_errors(
    tsv: Union[Path, str], schema: dict, report_type: ReportType = ReportType.STR
) -> List:
    tsv_path = Path(tsv)
    pre_flight_errors = _get_pre_flight_errors(tsv_path, schema=schema)
    if pre_flight_errors:
        return pre_flight_errors

    # assert (
    #     frictionless.__version__ == "4.0.0"
    # ), 'Upgrade dependencies: "pip install -r requirements.txt"'

    report = frictionless.validate(
        tsv_path, schema=schema, format="csv", checks=make_checks(schema)
    )

    assert len(report["errors"]) == 0, f"report has errors: {report}"
    assert "tasks" in report, f'"tasks" is missing: {report}'
    tasks = report["tasks"]
    assert len(tasks) == 1, f'"tasks" not single: {report}'
    task = tasks[0]
    assert "errors" in task, f'"tasks" missing "errors": {report}'

    schema_fields_dict = {field["name"]: field for field in schema["fields"]}

    return [
        _get_message(error, schema_fields_dict, report_type) for error in task["errors"]
    ]


def _get_pre_flight_errors(tsv_path: Path, schema: dict) -> Optional[List[str]]:
    try:
        dialect = csv.Sniffer().sniff(tsv_path.read_text())
    except csv.Error as e:
        return [str(e)]
    delimiter = dialect.delimiter
    expected_delimiter = "\t"
    if delimiter != expected_delimiter:
        return [
            f"Delimiter is {repr(delimiter)}, rather than expected {repr(expected_delimiter)}"
        ]

    # Re-reading the file is ugly, but creating a stream seems gratuitous.
    with tsv_path.open() as tsv_handle:
        reader = csv.DictReader(tsv_handle, dialect=dialect)
        fields = reader.fieldnames or []
        expected_fields = [f["name"] for f in schema["fields"]]
        if fields != expected_fields:
            errors = []
            fields_set = set(fields)
            expected_fields_set = set(expected_fields)
            extra_fields = fields_set - expected_fields_set

            if extra_fields:
                errors.append(f"Unexpected fields: {extra_fields}")
            missing_fields = expected_fields_set - fields_set
            if missing_fields:
                errors.append(f"Missing fields: {sorted(missing_fields)}")

            for i_pair in enumerate(zip(fields, expected_fields)):
                i, (actual, expected) = i_pair
                if actual != expected:
                    errors.append(
                        f'In column {i+1}, found "{actual}", expected "{expected}"'
                    )
            return errors

    return None


def _get_message(
    error: Dict[str, str],
    schema_fields: Dict[str, dict],
    report_type: ReportType = ReportType.STR,
) -> Union[str, Dict]:
    """
    >>> print(_get_message(
    ... {
    ...     'cell': 'bad-id',
    ...     'fieldName': 'orcid_id',
    ...     'fieldNumber': 6,
    ...     'fieldPosition': 6,
    ...     'rowNumber': 1,
    ...     'rowPosition': 2,
    ...     'note': 'constraint "pattern" is "fake-re"',
    ...     'message': 'The message from the library is a bit confusing!',
    ...     'description': 'A field value does not conform to a constraint.'
    ... },
    ... {
    ...     'orcid_id': {
    ...         'name': 'orcid_id',
    ...         'example': 'real-re'
    ...     }
    ... }))
    On row 2, column "orcid_id", value "bad-id" fails because\
 constraint "pattern" is "fake-re". Example: real-re

    """
    from ingest_validation_tools.validation_utils import get_json

    example = schema_fields.get(error.get("fieldName", ""), {}).get("example", "")

    return_str = report_type is ReportType.STR
    if "code" in error and error["code"] == "missing-label":
        msg = "Bug: Should have been caught pre-flight. File an issue."
        return msg if return_str else get_json(msg)
    if (
        "rowPosition" in error
        and "fieldName" in error
        and "cell" in error
        and "note" in error
    ):
        msg = (
            f'On row {error["rowPosition"]}, column "{error["fieldName"]}", '
            f'value "{error["cell"]}" fails because {error["note"]}'
            f'{f". Example: {example}" if example else example}'
        )
        return (
            msg
            if return_str
            else get_json(msg, error["rowPosition"], error["fieldName"])
        )
    return error["message"]


if __name__ == "__main__":
    import argparse
    from yaml import safe_load

    parser = argparse.ArgumentParser("CLI just for testing")
    parser.add_argument("--fixture", type=Path, required=True)
    args = parser.parse_args()
    tsv_path = args.fixture / "input.tsv"
    schema_path = args.fixture / "schema.yaml"
    errors = get_table_errors(tsv_path, safe_load(schema_path.read_text()))
    print("\n".join(errors))
