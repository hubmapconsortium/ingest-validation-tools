from __future__ import annotations

import json
import logging
import subprocess
from collections import Counter, defaultdict
from copy import copy
from datetime import datetime
from fnmatch import fnmatch
from functools import cached_property
from pathlib import Path
from typing import DefaultDict, Dict, List, Optional, Union
from urllib.parse import urljoin, urlsplit

import requests

from ingest_validation_tools.enums import DatasetType, OtherTypes, Sample
from ingest_validation_tools.error_report import ErrorDict, InfoDict
from ingest_validation_tools.local_validation.table_validator import (
    ReportType,
    get_table_errors,
)
from ingest_validation_tools.plugin_validator import (
    ValidatorError as PluginValidatorError,
)
from ingest_validation_tools.plugin_validator import (
    run_plugin_validators_iter,
)
from ingest_validation_tools.schema_loader import (
    AncestorTypeInfo,
    EntityTypeInfo,
    PreflightError,
    SchemaVersion,
    get_table_schema,
)
from ingest_validation_tools.validation_utils import (
    cedar_validation_call,
    get_data_dir_errors,
    get_entity_api_data,
    get_entity_type_vals,
    get_message,
    get_schema_version,
    read_rows,
)

TSV_SUFFIX = "metadata.tsv"
CONSTRAINTS_CHECK_METHOD = "ancestors"
CHECK_FIELDS = [
    "parent_sample_id",
    "parent_dataset_id",
    "source_id",
    "sample_id",
]


class Upload:
    def __init__(
        self,
        directory_path: Path,
        tsv_paths: list = [],
        dataset_ignore_globs: list = [],
        upload_ignore_globs: list = [],
        plugin_directory: Union[Path, None] = None,
        encoding: str = "utf-8",
        offline_only: bool = False,
        ignore_deprecation: bool = False,
        extra_parameters: Union[dict, None] = None,
        globus_token: str = "",
        run_plugins: Optional[bool] = None,
        app_context: dict = {},
        verbose: bool = True,
        report_type: ReportType = ReportType.STR,
        # TODO: remove add_notes from calls
        **kwargs,  # prevent blowing up if passed deprecated kwarg
    ):
        self.directory_path = directory_path
        # TODO: upstream seems to always pass in the following (with one exception), maybe make that the default
        # ignore_globs = [uuid, "extras", "*metadata.tsv", "validation_report.txt"]
        self.dataset_ignore_globs = dataset_ignore_globs
        # TODO: upstream seems to always pass in "*", maybe make that the default
        self.upload_ignore_globs = upload_ignore_globs
        self.plugin_directory = plugin_directory
        self.encoding = encoding
        self.offline_only = offline_only
        self.ignore_deprecation = ignore_deprecation
        self.extra_parameters = extra_parameters if extra_parameters else {}
        self.globus_token = globus_token
        self.run_plugins = run_plugins
        self.verbose = verbose
        self.report_type = report_type

        self.dataset_metadata = {}
        self.other_metadata = {}
        self.errors = ErrorDict()
        self.info = InfoDict()
        self.get_errors_called: bool = False
        self.get_info_called: bool = False

        self.get_app_context(app_context)

        try:
            """
            Get TSVs, set up or rule out multi-assay/
            shared uploads, ensure only single type for
            single-assay upload.
            """
            self.get_metadata_tsvs(tsv_paths)
            self._check_multi_assay()
            if not self.is_multi_assay:
                self._check_single_assay()
            self._check_shared_upload()
            self.shared_upload_non_global_paths

        except PreflightError as e:
            self.errors.preflight.value = str(e)

    ###################################
    #
    # Main public methods
    #
    ###################################

    def get_info(self) -> InfoDict:
        """
        If called before get_errors, will report dir schema major version only.
        """
        self.info.time = datetime.now()
        self.info.dir = str(self.directory_path)

        git_version = subprocess.check_output(
            "git rev-parse --short HEAD".split(" "),
            encoding="ascii",
            stderr=subprocess.STDOUT,
        ).strip()
        self.info.git = git_version

        tsvs = {
            Path(path).name: {
                "Metadata type": sv.dataset_type if sv.is_cedar else sv.table_schema,
                "Metadata version": sv.version,
                "Directory schema version": sv.dir_schema,
            }
            for path, sv in self.dataset_metadata.items()
        }
        self.info.tsvs = tsvs

        self.get_info_called = True
        return self.info

    def get_errors(self, **kwargs) -> ErrorDict:
        """
        This creates an ErrorDict object
        When converted using ErrorDict.as_dict(), keys are
        present only if there is actually an error to report.
        """
        # Return if PreflightErrors found
        if self.errors:
            return self.errors

        # Collect errors
        self.get_upload_errors()
        self.validate_metadata()
        self.get_directory_errors()
        self.get_reference_errors()
        self.get_file_errors(**kwargs | self.extra_parameters)

        self.get_errors_called = True
        return self.errors

    ###################################
    #
    # Top-level methods:
    #
    ###################################

    def get_metadata_tsvs(self, tsv_paths: List[str]):
        """
        Locate all dataset metadata TSV files at the top level of the upload.
        """
        unsorted_tsv_paths = {
            Path(path): get_schema_version(
                Path(path),
                self.encoding,
                self.app_context["entities_url"],
                self.app_context["ingest_url"],
                self.globus_token,
                self.directory_path,
            )
            for path in (tsv_paths if tsv_paths else self.directory_path.glob(f"*{TSV_SUFFIX}"))
        }

        self.dataset_metadata = {
            k: unsorted_tsv_paths[k] for k in sorted(unsorted_tsv_paths.keys())
        }
        if not self.dataset_metadata:
            self.errors.preflight.value = "There are no metadata TSVs."

    @cached_property
    def get_contributors(self):
        pass

    @cached_property
    def get_antibodies(self):
        pass

    def get_app_context(self, submitted_app_context: Dict):
        """
        Ensure that all default values are present, but privilege any
        submitted values (after making a basic validity check).
        """
        for url_type in ["entities_url", "ingest_url", "constraints_url", "uuid_url"]:
            if submitted_app_context.get(url_type):
                split_url = urlsplit(submitted_app_context[url_type])
                assert (
                    split_url.scheme and split_url.netloc
                ), f"{url_type} URL is incomplete: {submitted_app_context[url_type]}"
        self.app_context = {
            "entities_url": "https://entity.api.hubmapconsortium.org/entities/",
            "ingest_url": "https://ingest.api.hubmapconsortium.org/",
            "request_header": {"X-Hubmap-Application": "ingest-pipeline"},
            "constraints_url": None,
            "uuid_url": "https://uuid.api.hubmapconsortium.org/uuid/",
        } | submitted_app_context

    def get_upload_errors(self):
        """
        Check non-metadata/data dir elements required for uploads (contributors.tsv),
        or occurring at the top level (antibodies.tsv).
        """
        for path, schema in self.dataset_metadata.items():
            if "data_path" not in schema.rows[0] or "contributors_path" not in schema.rows[0]:
                self.errors.upload_metadata[f"{path} (as {schema.table_schema})"].append(
                    "File is missing data_path or contributors_path."
                )
            self._check_for_contact()
            self._check_other_tsvs(Path(path))

    def validate_metadata(
        self,
        tsv_paths: Dict[Path, SchemaVersion] = {},
    ):
        """
        Validate metadata.tsvs, both against Metadata Validator
        and any internal checks.
        """
        tsvs_to_evaluate = tsv_paths if tsv_paths else self.dataset_metadata
        for tsv_path, schema_version in tsvs_to_evaluate.items():
            if not schema_version.is_cedar:
                logging.info(
                    f"""TSV {tsv_path} does not contain a metadata_schema_id,
                    sending for local validation"""
                )
                self._local_validation(tsv_path, schema_version)
            elif not self.offline_only:
                self._online_checks(tsv_path, schema_version)

    def get_directory_errors(self):
        """
        Check directory schema of upload against current major version.
        """
        if self.is_multi_assay and self.multi_parent:
            if not self.multi_parent.dir_schema:
                self.errors.directory.update({self.multi_parent.path: "No directory schema found"})
                return
            # check only parent data_paths because parent has already been
            # confirmed to contain a complete set of childrens' data_paths
            self._check_dir_schema(
                self.multi_parent, self.multi_parent.path, self.multi_assay_data_paths
            )
            # Set dir schemas for child datasets to parent
            for schema in self.dataset_metadata.values():
                if not schema.dataset_type == self.multi_parent.dataset_type:
                    schema.dir_schema = self.multi_parent.dir_schema
        else:
            for path, schema in self.dataset_metadata.items():
                data_paths = self.__referenced_paths_by_tsv("data_path", path, schema)
                self._check_dir_schema(schema, Path(path), data_paths)

    def get_reference_errors(self):
        """
        Check all paths referenced in metadata TSVs against actual
        content of upload. Any unreferenced existing files, paths that
        are referenced multiple times (not in a shared/multi-assay upload),
        or errors with global/non_global shared file structure are reported.
        """
        if no_ref_errors := self.__get_no_ref_errors():
            self.errors.reference.update({"No References": no_ref_errors})
        if multi_ref_errors := self.__get_multi_ref_errors():
            self.errors.reference.update({"Multiple References": multi_ref_errors})
        if shared_dir_errors := self.__get_shared_dir_errors():
            self.errors.reference.update({"Shared Directory References": shared_dir_errors})

    def get_file_errors(self, **kwargs):
        """
        Run file-level validation. Plugin error checking is costly;
        by default this bails if other errors have been found already.
        Pass in run_plugins bool to modify behavior.
        """
        if self.run_plugins is None:  # default behavior
            if self.errors:  # errors found, skip
                self.errors.plugin_skip.value = (
                    "Skipping plugins validation: errors in upload metadata or dir structure."
                )
            else:  # no errors, run plugins
                logging.info("Running plugin validation...")
                self._get_plugin_errors(**kwargs)
        elif self.run_plugins:
            logging.info("Running plugin validation...")
            self._get_plugin_errors(**kwargs)
        else:
            logging.info("Skipping plugin validation.")

    ###################################
    #
    # Upload-level validation:
    #
    ###################################

    def _check_single_assay(self):
        types_counter = Counter([v.dataset_type for v in self.dataset_metadata.values()])
        if len(types_counter.keys()) > 1:
            raise PreflightError(
                f"Found multiple dataset types in upload: {', '.join(types_counter.keys())}"
            )
        repeated = [dataset_type for dataset_type, count in types_counter.items() if count > 1]
        if repeated:
            raise PreflightError(
                f"There is more than one TSV for this type: {', '.join(repeated)}"
            )

    def _check_shared_upload(self):
        self.is_shared_upload = {"global", "non_global"} == {
            x.name
            for x in self.directory_path.glob("*global")
            if x.is_dir() and x.name in ["global", "non_global"]
        }

    @cached_property
    def shared_upload_non_global_paths(self) -> dict:
        if not self.is_shared_upload:
            return {}
        non_global_paths = {}
        for tsv, schema in self.dataset_metadata.items():
            files = []
            for row in schema.rows:
                files.append([file.strip() for file in row.get("non_global_files").split(";")])
            non_global_paths[tsv] = files
        return non_global_paths

    def _check_other_tsvs(self, metadata_path: Path):
        """
        Validate antibodies/contributors files referenced in metadata TSVs.
        """
        for other_type in ["antibodies_path", "contributors_path"]:
            referenced_paths = self.__get_referenced_paths(other_type)
            for path_value, location_tuples in referenced_paths.items():
                other_path = self.directory_path / path_value
                rows = ", ".join([str(loc[1]) for loc in location_tuples])
                try:
                    assert other_path.exists()
                except AssertionError:
                    self.errors.upload_metadata[str(metadata_path)].append(
                        f"On row(s) {rows}, column '{other_type}', value '{path_value}' points to non-existent file: {other_path}"
                    )
                    continue
                try:
                    self._validate_non_metadata_tsv(other_path)
                except PreflightError as e:
                    self.errors.upload_metadata[str(metadata_path)].append(
                        f"On row(s) {rows}, column '{other_type}', error opening or reading value '{path_value}': {e.errors}"
                    )

    def _validate_non_metadata_tsv(self, other_path: Path):
        schema = get_schema_version(
            Path(other_path),
            self.encoding,
            self.app_context["entities_url"],
            self.app_context["ingest_url"],
            self.globus_token,
            self.directory_path,
        )
        self.other_metadata[other_path] = schema
        self.validate_metadata(tsv_paths={other_path: schema})

    def _check_for_contact(self):
        for path, schema in self.other_metadata.items():
            # If there is an is_contact field and a truthy
            # value present, is valid.
            if schema.rows[0].get("is_contact") and (
                "Yes" in [row.get("is_contact") for row in schema.rows]
            ):
                return
            self.errors.upload_metadata.update({path: "No primary contact."})

    ###################################
    #
    # Metadata validation:
    #
    ###################################

    def _online_checks(
        self,
        tsv_path: Path,
        schema: SchemaVersion,
    ):
        url_errors = self._get_url_errors(tsv_path, schema)
        if url_errors:
            self.errors.metadata_url_errors[tsv_path].extend(url_errors)
        try:
            api_errors = self._api_validation(schema)
        except Exception as e:
            api_errors = [e]
        if api_errors:
            self.errors.metadata_validation_api[tsv_path].extend(api_errors)
        constraint_errors = self._constraint_checks(schema)
        if constraint_errors:
            self.errors.metadata_constraint_errors[tsv_path].extend(constraint_errors)

    def _local_validation(self, tsv_path: Path, schema_version: SchemaVersion):
        try:
            schema = get_table_schema(
                schema_version,
                self.offline_only,
            )
        except Exception as e:
            self.errors.metadata_validation_local.update(
                {f"{tsv_path} (as {schema_version.table_schema})": [str(e)]}
            )
            return
        if schema.get("deprecated") and not self.ignore_deprecation:
            self.errors.metadata_validation_local.update(
                {
                    f"{tsv_path} (as {schema_version.table_schema})": [
                        "Schema version is deprecated"
                    ]
                }
            )
            return

        local_errors = get_table_errors(tsv_path, schema)
        if local_errors:
            self.errors.metadata_validation_local.update(
                {f"{tsv_path} (as {schema_version.table_schema})": local_errors}
            )

    def _api_validation(
        self,
        schema: SchemaVersion,
    ) -> List[Union[str, Dict]]:
        errors = []
        response = cedar_validation_call(schema.path)
        if response.status_code != 200:
            raise Exception(response.json())
        elif response.json().get("reporting") and len(response.json().get("reporting")) > 0:
            for error in response.json()["reporting"]:
                errors.append(get_message(error, self.report_type))
        else:
            logging.info(f"No errors found during CEDAR validation for {schema.path}!")
            logging.info(f"Response: {response.json()}.")
        return errors

    ###################################
    #
    # URL validation:
    #
    ###################################

    def _get_url_errors(self, tsv_path: Path, schema: SchemaVersion) -> List:
        """
        Check provided values for parent_sample_id and orcid_id; additionally
        check sample_id, organ_id, and source_id values in single TSV validation
        via validation_utils.get_tsv_errors.
        """
        constrained_fields = self._get_constrained_fields(schema)

        rows = read_rows(Path(tsv_path), self.encoding)
        fields = rows[0].keys()
        if missing_fields := [k for k in constrained_fields.keys() if k not in fields].sort():
            raise Exception(f"Missing fields: {missing_fields}")
        url_errors = self._find_and_check_url_fields(rows, constrained_fields, schema)
        return url_errors

    def _find_and_check_url_fields(
        self, rows: List, constrained_fields: Dict, schema: SchemaVersion
    ) -> List[Dict[str, str]]:
        errors = []
        for i, row in enumerate(rows):
            url_fields = self._get_url_fields(row, constrained_fields)
            for field_name, field_value in url_fields.items():
                for value in field_value:
                    try:
                        entity_type = self._check_url(
                            field_name, i, value, constrained_fields, schema
                        )
                        if entity_type:
                            schema.ancestor_entities.append(entity_type)
                    except Exception as e:
                        error = {
                            "errorType": type(e).__name__,
                            "column": field_name,
                            "row": i,
                            "value": value,
                            "error_text": e.__str__(),
                        }
                        errors.append(get_message(error, self.report_type))
        return errors

    def _check_url(
        self, field: str, row: int, value: str, constrained_fields: Dict, schema: SchemaVersion
    ) -> Optional[AncestorTypeInfo]:
        # TODO: clean up
        """
        Returns entity_type if checking a field in check_fields.
        """
        url = urljoin(constrained_fields[field], value)
        if field in CHECK_FIELDS:
            headers = self.app_context.get("request_header", {})
            response = get_entity_api_data(url, self.globus_token, headers)

            if schema.schema_name == DatasetType.DATASET and field == "parent_sample_id":
                origin_samples = response.json().get("origin_samples")
                if origin_samples is None and "direct_ancestor" in response.json():
                    origin_samples = response.json()["direct_ancestor"].get("origin_samples")
                if origin_samples is not None and isinstance(origin_samples, list):
                    for origin_sample in origin_samples:
                        if (
                            origin_sample.get("organ") == "OT"
                            or origin_sample.get("organ") == "UBERON:0010000"
                            or origin_sample.get("organ") is None
                        ):
                            raise Exception(
                                f"You are not allowed to register data against Sample {origin_sample.get('uuid')} with Organ Other. Please contact the respective help desk to ensure that appropriate support for your work can be provided."
                            )

            if (
                not (schema.schema_name == OtherTypes.SAMPLE and field == "sample_id")
                and not schema.schema_name == OtherTypes.SOURCE
            ):
                return AncestorTypeInfo(
                    entity_id=value,
                    source_schema=schema,
                    row=row,
                    column=field,
                    *get_entity_type_vals(response.json()),
                )
        elif field in ["orcid_id", "orcid"]:
            headers = {"Accept": "application/json"}
            response = requests.get(
                constrained_fields[field], headers=headers, params={"q": f"orcid:{value}"}
            )
            num_found = response.json().get("num-found")
            if num_found == 1:
                return
            elif num_found == 0:
                raise Exception(f"ORCID {value} does not exist.")
            else:
                raise Exception(f"Found {num_found} matches for ORCID {value}.")
        else:
            response = requests.get(url)
            response.raise_for_status()

    def _get_url_fields(
        self,
        row: Dict,
        constrained_fields: dict,
    ) -> Dict[str, List[str]]:
        url_fields = {}
        check = {k: v for k, v in row.items() if k in constrained_fields}
        for check_field, value in check.items():
            if check_field in CHECK_FIELDS and not self.globus_token:
                raise Exception("No token received to check URL fields against Entity API.")
            if check_field in ["parent_sample_id", "parent_dataset_id"]:
                url_fields[check_field] = value.split(",")
            else:
                url_fields[check_field] = [value]
        return url_fields

    ###################################
    #
    # Constraints validation:
    #
    ###################################

    def _constraint_checks(self, schema: SchemaVersion):
        if not self.app_context["constraints_url"]:
            return
        payload = self._construct_constraint_check(schema)
        if not payload:
            print(f"No constraint checks made for schema {schema.schema_name}.")
            return
        data = json.dumps(payload)
        headers = {
            "Authorization": f"Bearer {self.globus_token}",
            "Content-Type": "application/json",
        }
        params = {"match": True, "order": CONSTRAINTS_CHECK_METHOD}
        response = requests.post(
            self.app_context["constraints_url"], headers=headers, data=data, params=params
        )
        if self.verbose:
            print("Ancestor-Descendant pairs sent:")
            self._print_constraint_pairs(payload)
        try:
            response.raise_for_status()
        except Exception:
            return self._get_constraint_check_errors(response, schema)

    def _get_constrained_fields(self, schema: SchemaVersion):
        # assay -> parent_sample_id
        # sample -> sample_id
        # organ -> organ_id
        # contributors -> orcid (new) / orcid_id (old)

        constrained_fields = {}
        schema_name = schema.schema_name
        entities_url = self.app_context.get("entities_url")

        if schema_name in [
            OtherTypes.SOURCE,
            *Sample.with_parent_type(),
        ]:
            constrained_fields["source_id"] = entities_url
            if schema_name in Sample.with_parent_type():
                constrained_fields["sample_id"] = entities_url
        elif schema_name in OtherTypes.ORGAN:  # Deprecated, included for backward-compatibility
            constrained_fields["organ_id"] = entities_url
        elif schema_name == OtherTypes.CONTRIBUTORS:
            if schema.is_cedar:
                constrained_fields["orcid"] = "https://pub.orcid.org/v3.0/expanded-search/"
            else:
                constrained_fields["orcid_id"] = "https://pub.orcid.org/v3.0/expanded-search/"
        else:
            constrained_fields["parent_sample_id"] = entities_url
        return constrained_fields

    def _construct_constraint_check(self, schema: SchemaVersion) -> list[dict]:
        payload = []
        assert isinstance(schema.entity_type_info, EntityTypeInfo), Exception(
            f"Entity type info not present in {schema.schema_name} schema."
        )
        descendant_data = schema.entity_type_info.format_constraint_check_data()
        for ancestor_entity in schema.ancestor_entities:
            payload.append(
                {
                    "ancestors": ancestor_entity.format_constraint_check_data(),
                    "descendants": descendant_data,
                }
            )
        return payload

    def _print_constraint_pairs(self, constraint_list):
        for row in constraint_list:
            row_output = []
            for v in row.values():
                entity_type = v.get("entity_type")
                sub_type = v.get("sub_type")
                if type(sub_type) is list:
                    sub_type = ", ".join(sub_type)
                sub_type_val = v.get("sub_type_val")
                if type(sub_type_val) is list:
                    sub_type_val = ", ".join(sub_type_val)
                row_output.append(
                    f"{entity_type}{f'/{sub_type}' if sub_type else ''}{f'/{sub_type_val}' if sub_type_val else ''}"
                )
            print(" - ".join(row_output))

    def _get_constraint_check_errors(
        self,
        response: requests.Response,
        schema: SchemaVersion,
    ) -> List[str]:
        problem_entities = []
        assert schema.entity_type_info
        if response.status_code == 400:
            for i, entity_check in enumerate(response.json().get("description", [])):
                if entity_check["code"] != 200:
                    ancestors = schema.ancestor_entities[i].format_constraint_check_error()
                    error = {
                        "errorType": "Invalid Ancestor",
                        "column": schema.ancestor_entities[i].column,
                        "row": schema.ancestor_entities[i].row,
                        "value": schema.ancestor_entities[i].entity_id,
                        "error_text": f"Invalid ancestor type for TSV type {schema.entity_type_info.format_constraint_check_error()}. Data sent for ancestor {schema.ancestor_entities[i].entity_id}: {ancestors}.",
                    }
                    problem_entities.append(get_message(error, self.report_type))
        return problem_entities

    ###################################
    #
    # Directory validation:
    #
    ###################################

    def _check_dir_schema(
        self, schema_version: SchemaVersion, metadata_path: Path, data_path_refs: dict
    ):
        data_paths = list(data_path_refs.keys())
        dir_schema = schema_version.dir_schema
        if not dir_schema:
            self.errors.directory.update({schema_version.path: "No directory schema found"})
            return
        for data_path in data_paths:
            errors = {}
            dir = Path(self.directory_path)
            if data_path in self.shared_upload_non_global_paths:
                dir = Path(dir / "non_global")
            elif self.is_shared_upload:
                dir = Path(dir / "global")
            print_path = str(dir / data_path)

            try:
                ref_errors = get_data_dir_errors(
                    dir_schema,
                    root_path=self.directory_path,
                    data_dir_path=data_path,
                    dataset_ignore_globs=self.dataset_ignore_globs,
                ).popitem()
                if type(ref_errors[1]) is list:
                    errors[f"{print_path} (as {ref_errors[0]})"] = ref_errors[1]
                schema_version.dir_schema = ref_errors[0]
            except FileNotFoundError:
                self.errors.directory[str(metadata_path)].append(
                    f"On row {data_path_refs[data_path][0][1]}, column 'data_path', value '{data_path}' points to non-existent directory: {print_path}."
                )
            except Exception as e:
                errors[print_path] = e
            if errors:
                self.errors.directory.update(errors)

    ###################################
    #
    # Reference checks:
    #
    ###################################

    def __get_no_ref_errors(self) -> dict:
        """
        Files at the top level that are not referenced in any metadata TSV.
        """
        referenced_paths = (
            set(self.__get_referenced_paths("data_path").keys())
            | set(self.__get_referenced_paths("contributors_path").keys())
            | set(self.__get_referenced_paths("antibodies_path").keys())
        )
        referenced_data_paths = {Path(path) for path in referenced_paths}
        non_metadata_paths = {
            Path(path.name)
            for path in self.directory_path.iterdir()
            if not path.name.endswith(TSV_SUFFIX)
            and not any([fnmatch(path.name, glob) for glob in self.upload_ignore_globs])
        }
        unreferenced_paths = non_metadata_paths - referenced_data_paths

        errors = {}
        if unreferenced_dir_paths := [
            path for path in unreferenced_paths if Path(self.directory_path, path).is_dir()
        ]:
            errors["Directories"] = unreferenced_dir_paths
        if unreferenced_file_paths := [
            path for path in unreferenced_paths if not Path(self.directory_path, path).is_dir()
        ]:
            errors["Files"] = unreferenced_file_paths
        return errors

    def __get_multi_ref_errors(self) -> dict:
        """
        # Error if path is referenced multiple times, unless:
        - upload is a shared upload (shared paths validated elsewhere)
        - path is included in multi-assay upload paths (already validated)
        """
        if self.is_shared_upload:
            return {}
        errors = {}
        data_references = self.__get_referenced_paths("data_path")
        for path, references in data_references.items():
            if path not in self.multi_assay_data_paths:
                if len(references) > 1:
                    errors[path] = references
        return errors

    def __get_shared_dir_errors(self) -> dict:
        all_non_global_files = self.__get_referenced_paths("non_global_files")
        if all_non_global_files:
            errors = defaultdict(list)
            for row_non_global_files, row_references in all_non_global_files.items():
                row_non_global_files = {
                    (self.directory_path / "./non_global" / Path(x.strip())): x.strip()
                    for x in row_non_global_files.split(";")
                    if x.strip()
                }

                for (
                    full_path_row_non_global_file,
                    rel_path_row_non_global_file,
                ) in row_non_global_files.items():
                    if not full_path_row_non_global_file.exists():
                        row_refs = [
                            f"{tsv}, column 'non_global_files', row {row}"
                            for tsv, row in row_references
                        ]
                        errors[",".join(row_refs)].append(
                            f"In {full_path_row_non_global_file} does not exist in upload; is {rel_path_row_non_global_file} in the non_global directory?"
                        )
        else:
            # Catch case 2
            errors = {}
            if self.is_shared_upload:
                errors["Upload Errors"] = (
                    "No non_global_files specified but "
                    "upload has global & non_global directories"
                )

        return errors

    def __get_referenced_paths(self, col_name: str) -> dict[str, list[tuple[Path, int]]]:

        references = defaultdict(list)
        for tsv_path, schema in self.dataset_metadata.items():
            references.update(self.__referenced_paths_by_tsv(col_name, tsv_path, schema))
        return dict(references)

    def __referenced_paths_by_tsv(
        self, col_name: str, tsv_path: Path, schema: SchemaVersion
    ) -> dict[Path, list[tuple[str, int]]]:
        """
        Returns dict of path: [(referencing_tsv_path, row)]
        (col_name is already available wherever this was called)
        """
        references = defaultdict(list)
        for i, row in enumerate(schema.rows):
            if path_value := row.get(col_name):
                references[path_value].append((tsv_path, i + 2))
        return dict(references)

    ###################################
    #
    # File-level validation:
    #
    ###################################

    def _get_plugin_errors(self, **kwargs):
        plugin_path = self.plugin_directory
        if not plugin_path:
            return {}
        errors: DefaultDict[str, list] = defaultdict(list)
        for metadata_path, sv in self.dataset_metadata.items():
            try:
                # If this is not a multi-assay upload, check all files;
                # if this is a multi-assay upload, check all files ONCE
                # using the parent metadata file as a manifest, skipping
                # non-parent dataset_types
                if not self.multi_parent or (sv.dataset_type == self.multi_parent.dataset_type):
                    for k, v in run_plugin_validators_iter(
                        metadata_path,
                        sv,
                        plugin_path,
                        self.is_shared_upload,
                        verbose=self.verbose,
                        globus_token=self.globus_token,
                        app_context=self.app_context,
                        **kwargs,
                    ):
                        if v is None:
                            self.info.successful_plugins.append(k.__name__)
                        else:
                            errors[k.description].append(v)
            except PluginValidatorError as e:
                # We are ok with just returning a single error, rather than all.
                errors["Unexpected Plugin Error"] = [e]
        for k, v in errors.items():
            self.errors.plugin[k] = sorted(v)

    ###################################
    #
    # Multi-assay methods/properties:
    #
    ###################################

    @cached_property
    def multi_parent(self) -> Optional[SchemaVersion]:
        multi_assay_parents = [sv for sv in self.dataset_metadata.values() if sv.contains]
        if len(multi_assay_parents) == 0:
            return
        if len(multi_assay_parents) > 1:
            raise PreflightError(
                f"Upload contains multiple parent multi-assay types: {', '.join([parent.schema_name for parent in multi_assay_parents])}"
            )
        return multi_assay_parents[0]

    @cached_property
    def multi_components(self) -> List:
        if self.multi_parent:
            return [sv for sv in self.dataset_metadata.values() if not sv.contains]
        else:
            return []

    @cached_property
    def multi_assay_data_paths(self) -> dict:
        if not self.is_multi_assay or not self.multi_parent:
            return {}
        shared_data_paths = {
            key["data_path"]: row + 2 for row, key in enumerate(self.multi_parent.rows)
        }
        return shared_data_paths

    @cached_property
    def is_multi_assay(self) -> bool:
        if self.multi_parent and self.multi_components:
            return True
        return False

    def _check_multi_assay(self):
        # This is not recursive, so if there are nested multi-assay types it will not work
        if self.multi_parent and self.multi_components:
            try:
                self._check_multi_assay_components()
                self._check_data_paths_shared_with_parent()
                logging.info(f"Multi-assay parent: {self.multi_parent.dataset_type}")
                logging.info(
                    f"Multi-assay components: {', '.join([component.dataset_type for component in self.multi_components])}"  # noqa: E501
                )
            except AssertionError as e:
                raise PreflightError(str(e))
        else:
            logging.info("Not a multi-assay upload.")

    def _check_multi_assay_components(self):
        """
        Iterate through child dataset types, check that they are valid
        components of parent multi-assay type and that no components are missing
        """
        assert (
            self.multi_parent and self.multi_components
        ), f"Error validating multi-assay upload, missing parent and/or component values. Parent: {self.multi_parent.dataset_type if self.multi_parent else None} / Components: {[component.dataset_type for component in self.multi_components if self.multi_components]}"  # noqa: E501
        not_allowed = []
        necessary = copy(self.multi_parent.contains)
        for sv in self.multi_components:
            if sv.dataset_type.lower() not in self.multi_parent.contains:
                not_allowed.append(sv.dataset_type)
            else:
                necessary.remove(sv.dataset_type.lower())
        message = ""
        if necessary:
            message += f"Multi-assay parent type {self.multi_parent.dataset_type} missing required component(s): {', '.join(necessary)}."  # noqa: E501
        if not_allowed:
            message += f" Invalid child assay type(s) for parent type {self.multi_parent.dataset_type}: {', '.join(not_allowed)}"  # noqa: E501
        if message:
            raise PreflightError(message)

    def _check_data_paths_shared_with_parent(self):
        """
        Check parent multi-assay TSV data_path values against data_paths in child TSVs
        """
        assert (
            self.multi_parent and self.multi_components
        ), f"Cannot check shared data paths for multi-assay upload, missing parent and/or component values. Parent: {self.multi_parent.dataset_type if self.multi_parent else None} / Components: {[component.dataset_type for component in self.multi_components if self.multi_components]}"  # noqa: E501
        # Make sure that neither parents nor components have any unique paths, as this
        # indicates either a missing component or a dataset that is unique to a
        # component; collect any/all errors
        errors = []
        for component in self.multi_components:
            component_paths = {row.get("data_path") for row in component.rows}
            unique_in_component = component_paths.difference(self.multi_assay_data_paths.keys())
            if unique_in_component:
                errors.append(
                    f"Path(s) in {component.dataset_type} metadata TSV not present in parent: {', '.join(unique_in_component)}."
                )
            unique_in_parent = set(self.multi_assay_data_paths.keys()).difference(component_paths)
            if unique_in_parent:
                errors.append(
                    f"Path(s) in {self.multi_parent.dataset_type} metadata TSV not present in component {component.dataset_type}: {', '.join(unique_in_parent)}."  # noqa: E501
                )
        if errors:
            raise PreflightError(" ".join(errors))
