import re
from string import Template
from sys import stderr
from typing import Any, Callable, Iterator
from urllib.parse import urljoin

import frictionless
import requests

ErrorIterator = Iterator[frictionless.errors.CellError]
Row = dict[str, Any]
Check = Callable[[Row], ErrorIterator]


class CheckFactory:
    def __init__(self, schema: dict, status_cache: dict):
        """
        status_cache is instantiated on a per-Upload basis,
        prevents repeated requests to the same endpoint
        when just checking for a status.
        """
        self.schema = schema
        self.status_cache = status_cache
        self._prev_value_run_length = {}

    def make_checks(self) -> list[Check]:
        return [
            self.make_url_check(),
            self.make_sequence_limit_check(),
            self.make_units_check(),
            self.make_forbid_na_check(),
        ]

    def _get_constrained_fields(self, constraint: str) -> dict[str, list | dict]:
        c_c = "custom_constraints"
        return {
            f["name"]: f[c_c][constraint]
            for f in self.schema["fields"]
            if c_c in f and constraint in f[c_c]
        }

    def _check_url_status_cache(self, url: str) -> str:
        if status := self.status_cache.get(url):
            return status

        print(f"Fetching un-cached url: {url}", file=stderr)
        try:
            response = requests.get(url, allow_redirects=True)
            self.status_cache[url] = str(response.status_code)
        except Exception as e:
            self.status_cache[url] = str(e)
        return self.status_cache[url]

    # Map any updated prefix URLs in table-schema files to (prefix, suffix) where suffix
    # can be "" or None
    LEGACY_URL_MAP: dict[str, tuple[str, str | None]] = {
        "https://scicrunch.org/resolver/RRID:": ("https://scicrunch.org/resolver/", ".json"),
        "https://dx.doi.org/:": ("https://doi.org/api/handle/", None),
    }

    def make_url_check(self, template=Template('URL returned $status: "$url"')) -> Check:
        url_constrained_fields = self._get_constrained_fields("url")

        def url_check(row):
            for k, v in row.items():
                if v is None:
                    continue
                if k in url_constrained_fields:
                    prefix = url_constrained_fields[k]["prefix"]  # type: ignore
                    if mapped_url := self.LEGACY_URL_MAP.get(prefix):
                        url = urljoin(mapped_url[0], v)
                        if suffix := mapped_url[1]:
                            url = f"{url}{suffix}"
                    else:
                        url = f"{prefix}{v}"
                    status = self._check_url_status_cache(url)
                    if status != "200":
                        note = template.substitute(status=status, url=url)
                        yield frictionless.errors.CellError.from_row(row, note=note, field_name=k)

        return url_check

    def make_sequence_limit_check(
        self,
        template=Template(
            "there is a run of $run_length sequential items: Limit is $limit. "
            "If correct, reorder rows."
        ),
    ) -> Check:
        sequence_limit_fields = self._get_constrained_fields("sequence_limit")

        def sequence_limit_check(row):
            prefix_number_re = r"(?P<prefix>.*?)(?P<number>\d+)$"
            for k, v in row.items():
                # If the schema declares the field as datetime,
                # "v" will be a python object, and regexes will error.
                v = str(v)

                if k not in sequence_limit_fields or not v:
                    continue

                match = re.search(prefix_number_re, v)
                if not match:
                    if k in self._prev_value_run_length:
                        del self._prev_value_run_length[k]
                    continue

                if k not in self._prev_value_run_length:
                    self._prev_value_run_length[k] = (v, 1)
                    continue

                prev_value, run_length = self._prev_value_run_length[k]
                prev_match = re.search(prefix_number_re, prev_value)
                if prev_match and (
                    match.group("prefix") != prev_match.group("prefix")
                    or int(match.group("number")) != int(prev_match.group("number")) + 1
                ):
                    self._prev_value_run_length[k] = (v, 1)
                    continue

                run_length += 1
                self._prev_value_run_length[k] = (v, run_length)

                limit = sequence_limit_fields[k]
                assert isinstance(limit, int)
                assert limit > 1, "The lowest allowed limit is 2"
                if run_length >= limit:
                    note = template.substitute(run_length=run_length, limit=limit)
                    yield frictionless.errors.CellError.from_row(row, note=note, field_name=k)

        return sequence_limit_check

    def make_units_check(
        self, template=Template("it requires a value when $units_for is filled")
    ) -> Check:
        units_constrained_fields = self._get_constrained_fields("units_for")

        def units_check(row):
            for k, _ in row.items():
                if k in units_constrained_fields:
                    units_for = units_constrained_fields[k]
                    if (row[units_for] or row[units_for] == 0) and not row[k]:
                        note = template.substitute(units_for=units_for)
                        yield frictionless.errors.CellError.from_row(row, note=note, field_name=k)

        return units_check

    def make_forbid_na_check(
        self, template=Template('"N/A" fields should just be left empty')
    ) -> Check:
        forbid_na_constrained_fields = self._get_constrained_fields("forbid_na")

        def forbid_na_check(row):
            for k, v in row.items():
                if (
                    k in forbid_na_constrained_fields
                    and isinstance(v, str)
                    and v.upper() in ["NA", "N/A"]
                ):
                    note = template.substitute()
                    yield frictionless.errors.CellError.from_row(row, note=note, field_name=k)

        return forbid_na_check
