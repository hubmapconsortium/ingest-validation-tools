import difflib
import glob
import json
import re
import unittest
from io import TextIOWrapper
from pathlib import Path
from unittest.mock import patch

from parameterized import parameterized
from yaml import dump

from ingest_validation_tools.error_report import ErrorTypes, ValidationSerializer
from ingest_validation_tools.schema_loader import PreflightError, SchemaVersion
from ingest_validation_tools.table_validator import ReportType
from ingest_validation_tools.upload import Upload
from tests.fixtures import (
    SCATACSEQ_BOTH_VERSIONS_VALID,
    SCATACSEQ_HIGHER_VERSION_VALID,
    SCATACSEQ_LOWER_VERSION_VALID,
    SCATACSEQ_NEITHER_VERSION_VALID,
)

CONSTRAINTS_URL = "http://constraints_test/"
ENTITIES_URL = "http://entities_test/"

SHARED_OPTS = {
    "encoding": "ascii",
}
DATASET_EXAMPLES_OPTS: dict = SHARED_OPTS | {
    "dataset_ignore_globs": ["ignore-*.tsv", ".*"],
    "upload_ignore_globs": ["drv_ignore_*"],
}
DATASET_IEC_EXAMPLES_OPTS = SHARED_OPTS | {
    "dataset_ignore_globs": ["metadata.tsv"],
    "upload_ignore_globs": ["*"],
}
PLUGIN_EXAMPLES_OPTS = DATASET_EXAMPLES_OPTS | {
    "plugin_directory": "../ingest-validation-tests/src/ingest_validation_tests/",
    "run_plugins": True,
}


class MockException(Exception):
    def __init__(self, error):
        super().__init__(error)


class TokenException(Exception):
    def __init__(self, error):
        super().__init__(error)

    # def __init__(self, error: str, clean_report: Union[str, Dict]):
    #     super().__init__(error)
    #     self.clean_report = clean_report


def mutate_upload_errors_with_fixtures(upload: Upload, test_dir: str) -> Upload:
    for tsv_path, schema in upload.effective_tsv_paths.items():
        fixtures = get_online_check_fixtures(schema.schema_name, test_dir)
        if url_errors := fixtures.get(ErrorTypes.METADATA_VALIDATION_URLS, []):
            for error in url_errors:
                upload.errors(ErrorTypes.METADATA_VALIDATION_URLS, error, file=tsv_path)
        if api_errors := fixtures.get(ErrorTypes.METADATA_VALIDATION_API, []):
            for error in api_errors:
                upload.errors(ErrorTypes.METADATA_VALIDATION_API, error, file=tsv_path)
        for other_type, paths in {
            "antibodies": schema.antibodies_paths,
            "contributors": schema.contributors_paths,
        }.items():
            for path in paths:
                other_fixtures = get_online_check_fixtures(other_type, test_dir)
                other_url_errors = other_fixtures.get(ErrorTypes.METADATA_VALIDATION_URLS, {})
                if other_url_errors:
                    for error in other_url_errors:
                        upload.errors(ErrorTypes.METADATA_VALIDATION_URLS, error, file=path)
                other_api_errors = other_fixtures.get(ErrorTypes.METADATA_VALIDATION_API, {})
                if other_api_errors:
                    for error in other_api_errors:
                        upload.errors(ErrorTypes.METADATA_VALIDATION_API, error, file=path)
    return upload


def dataset_test(
    test_dir: str,
    dataset_opts: dict,
    verbose: bool = False,
    globus_token: str = "",
    # TODO: do we need both of these params
    offline: bool = False,
    use_online_check_fixtures: bool = False,
):
    dataset_opts = dataset_opts | {"verbose": verbose}
    print(f"Testing {test_dir}...")
    readme = open(f"{test_dir}/README.md", "r")
    if offline:
        upload = TestDatasetExamples.prep_offline_upload(test_dir, dataset_opts)
    else:
        upload = Upload(Path(f"{test_dir}/upload"), globus_token=globus_token, **dataset_opts)
    if use_online_check_fixtures:
        upload = mutate_upload_errors_with_fixtures(upload, test_dir)
    upload.validate(detailed_success_report=True)
    if upload.report.valid:
        upload.validator.report.git = "WILL_CHANGE"
        upload.validator.report.time = "WILL_CHANGE"  # type: ignore
        # This code exists to format the validation report to match current formatting
        # because testing needs an overhaul so rewriting all READMEs is not timely
        dict_report = upload.validator.validation_report()
        dict_report["Directory"] = dict_report["Base path"]
        dict_report["TSVs"] = dict_report["TSVs"]
        dict_report.pop("Base path")
        dict_report.pop("Valid")
        report = "No errors!\n" + dump(dict_report)
    else:
        report = dump(upload.validate(as_yaml=True))
    diff_test(test_dir, readme, report, verbose=verbose)
    readme.close()
    if "PreflightError" in report:
        raise MockException(
            f"Error report for {test_dir} contains PreflightError, do not make assertions about calls."
        )


def dev_url_replace(original_str: str):
    dev_regex = re.compile(r"-api.dev")
    new_str = re.sub(dev_regex, ".api", original_str)
    return new_str


def color_code_diff(a: str, b: str, color: bool = True) -> bool:
    old = "\x1b[0;37;41m" if color else "<--removed-->"
    new = "\x1b[0;37;42m" if color else "<++added++>"
    reset = "\x1b[0m" if color else "</>"
    m = difflib.SequenceMatcher(a=a, b=b)
    diff = bool(m.ratio())
    if diff:
        print(
            f"""

              DIFF
              {f"{old}README{reset} => {new}Validation Report{reset}"}
              """
        )
        for tag, i1, i2, j1, j2 in m.get_opcodes():
            if tag == "replace":
                print(old, a[i1:i2], reset, end="")
                print(new, b[j1:j2], reset, end="")
            if tag == "delete":
                print(old, a[i1:i2], reset, end="")
            if tag == "insert":
                print(new, b[j1:j2], reset, end="")
            if tag == "equal":
                print(a[i1:i2], end="")
        print()
    return diff


def diff_test(
    test_dir: str,
    readme: TextIOWrapper,
    report: str,
    verbose: bool = True,
    env: str = "PROD",
    color: bool = True,
):
    if env == "DEV":
        report = dev_url_replace(report)
    # Remove quotes and ticks from readme
    read_readme = " ".join(
        [line.strip().replace("'", "") for line in readme.readlines() if "```" not in line]
    )
    # Remove quotes as well as whitespace and dashes from YAML formatting
    cleaned_report = [
        line.strip(" -").strip().replace("'", "").strip() for line in report.splitlines()
    ]
    read_report = " ".join([line for line in cleaned_report if len(line) > 0])
    # Only count added/removed lines, better than dealing with context_diff control chars
    diff = color_code_diff(read_readme, read_report, color=color)
    readme.close()
    # TODO: switch to dict comparison, requires rewriting all READMEs
    # diff = DeepDiff(readme, report)
    # print_diff = []
    # if verbose:
    # for val in diff.values():
    #     for val in val.values():
    #         print_diff.append({"old_value": val["old_value"], "new_value": val["new_value"]})
    if verbose:
        msg = f"""
        {color_code_diff(read_readme, read_report, color=False)}

                If new version is correct, overwrite previous README.md and fixtures.json files by running:
                    env PYTHONPATH=src:$PYTHONPATH python -m tests-manual.update_test_data -t {test_dir} -g <globus_token>

                For help / other options:
                    env PYTHONPATH=src:$PYTHONPATH python -m tests-manual.update_test_data --help
                """
    else:
        msg = f"""
    FAILED diff_test: {test_dir}. Run for more detailed output:
        env PYTHONPATH=src:$PYTHONPATH python -m tests-manual.update_test_data -t {test_dir} --globus_token "" --manual_test --dry_run --verbose
    """
    assert not diff, msg
    print(f"PASSED diff_test: {test_dir}")


def _open_and_read_fixtures_file(path: str) -> dict:
    try:
        with open(Path(path) / "fixtures.json") as f:
            opened = json.load(f)
            f.close()
    except json.JSONDecodeError:
        return {}
    return opened


def get_online_check_fixtures(schema_name: str, dir_path: str) -> dict:
    fixture = _open_and_read_fixtures_file(dir_path)
    value = fixture.get("validation", {}).get(schema_name, {})
    if value is None:
        return {}
    return value


def assaytype_side_effect(path: str, row: dict, *args, **kwargs):
    del args, kwargs
    response_dict = _open_and_read_fixtures_file(path)
    dataset_type = row.get("assay_type") if row.get("assay_type") else row.get("dataset_type")
    return response_dict.get("assaytype", {}).get(dataset_type)


def dir_schema_side_effect(dir_schema: str, fixture_data: dict):
    directory_schema_minor_versions = [key for key in fixture_data if key.startswith(dir_schema)]
    if not directory_schema_minor_versions:
        return None
    else:
        return fixture_data


class TestDatasetExamples(unittest.TestCase):
    dataset_test_dirs = [
        test_dir
        for test_dir in [
            *glob.glob("examples/dataset-examples/**"),
            *glob.glob("examples/dataset-iec-examples/**"),
        ]
        if Path(test_dir).is_dir()
    ]
    errors = []

    def setUp(self):
        super().setUp()
        self.get_paths()

        def tearDown(self):
            error_lines = "\n".join([str(error) for error in self.errors])
            errors = " ".join([str(error) for error in self.errors])
            try:
                self.assertEqual([], self.errors)
            except AssertionError as e:
                print(
                    f"""
                    -------ERRORS-------
                    {error_lines}

                    Run for more detailed output:
                        env PYTHONPATH=src:$PYTHONPATH python -m tests-manual.update_test_data -t {errors} --verbose --globus_token "" --manual_test --dry_run
                    """
                )
                raise e

    def get_paths(self):
        self.dataset_paths = {}
        # for test_dir in self.dataset_test_dirs:
        #     metadata_paths = [path for path in Path(f"{test_dir}/upload").glob("*metadata.tsv")]
        #     self.dataset_paths[test_dir] = metadata_paths
        self.dataset_paths["examples/dataset-examples/bad-mixed"] = [
            "examples/dataset-examples/bad-mixed/upload/metadata.tsv"
        ]

    def test_validate_dataset_examples(self, verbose: bool = False):
        breakpoint()
        for test_dir in self.dataset_paths.keys():
            with self.subTest(test_dir=test_dir):
                if "dataset-examples" in test_dir:
                    opts = DATASET_EXAMPLES_OPTS
                elif "dataset-iec-examples" in test_dir:
                    opts = DATASET_IEC_EXAMPLES_OPTS
                elif "plugin-tests" in test_dir:
                    opts = PLUGIN_EXAMPLES_OPTS
                else:
                    opts = {}
                with patch("ingest_validation_tools.validation_utils.get_assaytype_data"):
                    with patch("ingest_validation_tools.upload.Upload._get_url_errors"):
                        try:
                            dataset_test(
                                test_dir,
                                opts,
                                # verbose=verbose,
                                verbose=True,
                                offline=True,
                                use_online_check_fixtures=True,
                            )
                        except MockException as e:
                            print(e)
                        except AssertionError as e:
                            print(e)
                            self.errors.append(test_dir)
            break

    @staticmethod
    def prep_offline_upload(test_dir: str, opts: dict) -> Upload:
        with patch(
            "ingest_validation_tools.validation_utils.get_assaytype_data",
            side_effect=lambda row, ingest_url, globus_token: assaytype_side_effect(
                test_dir, row, ingest_url, globus_token
            ),
        ):
            with patch("ingest_validation_tools.validation_utils.get_entity_api_data"):
                with patch("ingest_validation_tools.upload.Upload.online_checks"):
                    upload = Upload(Path(f"{test_dir}/upload"), **opts)
                    upload.get_errors()
                    upload = mutate_upload_errors_with_fixtures(upload, test_dir)
                    return upload

    def prep_dir_schema_upload(self, test_dir: str, opts: dict, patch_data: dict) -> Upload:
        with patch(
            "ingest_validation_tools.validation_utils.get_assaytype_data",
            side_effect=lambda row, ingest_url, globus_token: assaytype_side_effect(
                test_dir, row, ingest_url, globus_token
            ),
        ):
            with patch(
                "ingest_validation_tools.validation_utils.get_possible_directory_schemas",
                side_effect=lambda dir_schema: dir_schema_side_effect(dir_schema, patch_data),
            ) as dir_schemas_func_patch:
                with patch("ingest_validation_tools.upload.Upload.online_checks"):
                    upload = Upload(Path(f"{test_dir}/upload"), **opts)
                    for val in upload.effective_tsv_paths.values():
                        val.dir_schema = "test-schema-v0"
                    upload.get_errors()
                    dir_schemas_func_patch.assert_called()
                    return upload

    @parameterized.expand(
        [
            ([DATASET_EXAMPLES_OPTS, SCATACSEQ_HIGHER_VERSION_VALID], "test-schema-v0.1", None),
            ([DATASET_EXAMPLES_OPTS, SCATACSEQ_LOWER_VERSION_VALID], "test-schema-v0.0", None),
            ([DATASET_EXAMPLES_OPTS, SCATACSEQ_BOTH_VERSIONS_VALID], "test-schema-v0.1", None),
            (
                [DATASET_EXAMPLES_OPTS, SCATACSEQ_NEITHER_VERSION_VALID],
                "test-schema-v0",
                "No matching directory schemas found.",
            ),
        ]
    )
    def test_data_dir_versions(self, fixtures, expected_dir_schema, errors_to_check):
        test_dirs = [
            "examples/dataset-examples/bad-scatacseq-data",
            "examples/dataset-examples/good-scatacseq-metadata-v0",
        ]
        for test_dir in test_dirs:
            upload = self.prep_dir_schema_upload(test_dir, *fixtures)
            for path in upload.effective_tsv_paths.keys():
                dir_schema_version = upload.report.tsvs.get(Path(path).name, {}).get(
                    "Directory schema version"
                )
                self.assertEqual(dir_schema_version, expected_dir_schema)
                if errors_to_check is not None:
                    error_report = list(
                        json.loads(upload.validate(format_type=ReportType.JSON)).values()  # type: ignore
                    )[0]
                    dir_errors = error_report[ErrorTypes.DIRECTORY.value][0]
                    error = dir_errors[f"dataset-1 (as schema '{expected_dir_schema}')"][0].get(
                        "errorContent"
                    )
                    assert (
                        error == errors_to_check
                    ), f"Actual error {error} != expected error {errors_to_check}"

    def get_schema_side_effect(
        self, tsv_path, encoding, entities_url, ingest_url, globus_token, directory_path
    ):
        del encoding, entities_url, ingest_url, globus_token, directory_path
        schema_map = {
            "repeated_parent_fake_path_1": SchemaVersion(
                schema_name="visium-no-probes", contains=["histology", "rnaseq"]
            ),
            "repeated_parent_fake_path_2": SchemaVersion(
                schema_name="visium-no-probes", contains=["histology", "rnaseq"]
            ),
            "unique_parent_fake_path_1": SchemaVersion(
                schema_name="visium-no-probes", contains=["histology", "rnaseq"]
            ),
            "unique_parent_fake_path_2": SchemaVersion(schema_name="histology"),
        }
        return schema_map.get(str(tsv_path))

    def test_bad_multi_assay_parents(self):
        with patch(
            "ingest_validation_tools.validation_utils.get_assaytype_data",
        ):
            with patch("ingest_validation_tools.upload.Upload.online_checks"):
                with patch(
                    "ingest_validation_tools.upload.get_schema_version",
                    side_effect=lambda tsv_path, encoding, entities_url, ingest_url, globus_token, directory_path: self.get_schema_side_effect(
                        tsv_path, encoding, entities_url, ingest_url, globus_token, directory_path
                    ),
                ):
                    bad_upload = Upload(
                        Path("test_path"),
                        tsv_paths=["repeated_parent_fake_path_1", "repeated_parent_fake_path_2"],
                        **DATASET_EXAMPLES_OPTS,
                    )
                    with self.assertRaises(PreflightError):
                        bad_upload.multi_parent
                    good_upload = Upload(
                        Path("test_path"),
                        tsv_paths=["unique_parent_fake_path_1", "unique_parent_fake_path_2"],
                        **DATASET_EXAMPLES_OPTS,
                    )
                    self.assertEqual(
                        good_upload.multi_parent,
                        SchemaVersion(
                            schema_name="visium-no-probes", contains=["histology", "rnaseq"]
                        ),
                    )

    def test_counts(self):
        test_dirs = {
            "examples/dataset-examples/bad-cedar-assay-histology": {
                "Spreadsheet Validator Errors": 2,
                "URL Check Errors": 1,
                "No References": 1,
                "Plugins Skipped": True,
            },
            "examples/dataset-examples/good-scatacseq-metadata-v0": {},
            "examples/dataset-examples/bad-mixed": {
                "Preflight Errors": "Found multiple dataset types in upload: CODEX, SNARE-seq2"
            },
        }
        for test_dir, expected_counts in test_dirs.items():
            upload = self.prep_offline_upload(test_dir, DATASET_EXAMPLES_OPTS)
            report = ValidationSerializer(
                upload.report, plugins_ran=bool(upload.run_plugins), as_yaml=True
            )
            self.assertEqual(report.count_errors_by_category(), expected_counts)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDatasetExamples)
    suite.debug()
