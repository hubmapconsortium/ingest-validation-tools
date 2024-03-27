from pathlib import Path
from typing import Dict

from ingest_validation_tools.schema_loader import PreflightError
from ingest_validation_tools.upload import Upload
from ingest_validation_tools.validation_utils import get_schema_version


class SingleTSV(Upload):
    def __init__(
        self,
        tsv_path: str,
        encoding: str = "utf-8",
        globus_token: str = "",
        app_context: dict = {},
    ):
        self.encoding = encoding
        self.errors = {}
        self.tsv_path = tsv_path
        self.effective_tsv_paths = {}
        self.globus_token = globus_token
        self.optional_fields = {}
        self.offline = False
        self.ignore_deprecation = False

        self.get_app_context(app_context)

        try:
            self.effective_tsv_paths = {
                tsv_path: get_schema_version(
                    Path(tsv_path),
                    self.encoding,
                    self.app_context["ingest_url"],
                )
            }

        except PreflightError as e:
            self.errors["Preflight"] = e

    def format_error(self, error_dict: Dict):
        if len(error_dict) == 1:
            for key, value in error_dict.values():
                if value.get(self.tsv_path):
                    return value[self.tsv_path]
                for key in value.keys():
                    if self.tsv_path in key:
                        return value[key]
        return error_dict
