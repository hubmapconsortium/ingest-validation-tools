import os
import re
from glob import glob
from pathlib import Path
from textwrap import dedent

from vcr import VCR
from vcr.request import Request

from ingest_validation_tools.error_report import ErrorReport
from ingest_validation_tools.upload import Upload
from tests.manual.updaters import UpdateReadme

# import logging
# logging.basicConfig()
# vcr_log = logging.getLogger("vcr")
# vcr_log.setLevel(logging.INFO)

SHARED_OPTS: dict = {
    "encoding": "ascii",
    "globus_token": "offline_test",
}
DATASET_EXAMPLES_OPTS: dict = SHARED_OPTS | {
    "dataset_ignore_globs": ["ignore-*.tsv", ".*"],
    "upload_ignore_globs": ["drv_ignore_*"],
}
DATASET_IEC_EXAMPLES_OPTS: dict = SHARED_OPTS | {
    "dataset_ignore_globs": ["metadata.tsv"],
    "upload_ignore_globs": ["*"],
}
PLUGIN_EXAMPLES_OPTS: dict = DATASET_EXAMPLES_OPTS | {
    "plugin_directory": "../ingest-validation-tests/src/ingest_validation_tests/",
    "run_plugins": True,
    "offline_only": True,
}


def get_example_paths() -> list[Path]:
    return [
        Path(test_dir)
        for test_dir in [
            *glob("examples/dataset-examples/**"),
            *glob("examples/dataset-iec-examples/**"),
        ]
        if Path(test_dir).is_dir()
    ]


def create_upload(dataset_path: Path, globus_token: str) -> Upload:
    if "dataset-examples" in dataset_path.parts:
        opts = DATASET_EXAMPLES_OPTS
    elif "dataset-iec-examples" in dataset_path.parts:
        opts = DATASET_IEC_EXAMPLES_OPTS
    elif "plugin-tests" in dataset_path.parts:
        opts = PLUGIN_EXAMPLES_OPTS
    else:
        opts = {}
    if globus_token:
        opts["globus_token"] = globus_token
    return Upload(Path(f"{dataset_path}/upload"), **opts)


def clear_cassette(test_dir: Path):
    cassette = Path(test_dir / "fixtures.json")
    if cassette.exists():
        print(f"Deleting cassette {cassette}")
        os.remove(cassette)


def vcr_create_upload_and_diff(
    test_dir: Path,
    globus_token: str,
    record_mode: str,
    verbose: bool = True,
    dry_run: bool = True,
    vcr: VCR | None = None,
) -> str | None:
    my_vcr = vcr or VCR(serializer="json")
    my_vcr.register_matcher("validation_matcher", validation_matcher)
    if record_mode == "all":
        clear_cassette(test_dir)
    with my_vcr.use_cassette(
        path=test_dir / "fixtures.json",
        record_mode=record_mode,
        decode_compressed_response=True,
        # allow_playback_repeats=True,
        match_on=["validation_matcher"],
    ):
        upload = create_upload(test_dir, globus_token)
        upload.get_errors()
    updater = UpdateReadme(test_dir, dry_run, verbose, ErrorReport(upload))
    return updater.check_maybe_write_readme()


def validation_matcher(r1, r2):
    assert r1.uri == r2.uri
    assert r1.method == r2.method
    if "validate-tsv" in r1.uri:
        cleaned_r1 = remove_file_upload_hash(r1)
        cleaned_r2 = remove_file_upload_hash(r2)
        assert cleaned_r1.body == cleaned_r2.body
        return
    assert r1.body == r2.body


def remove_file_upload_hash(request: Request) -> Request:
    if "validate-tsv" in request.url and isinstance(request.body, bytes):
        request_body = request.body.decode("utf-8")
        prefix = re.match(r"--.*\s", request_body)
        suffix = re.search(r"--\S*--", request_body)
        if prefix and suffix and prefix.group(0) and suffix.group(0):
            new_body = request_body.replace(prefix.group(0), "").replace(suffix.group(0), "")
            request.body = new_body.encode("utf-8")
    return request


def test_dataset_examples(test_dirs: list[Path], dry_run: bool = True, verbose: bool = True):
    """
    Test example dataset directories using fixture cassettes.
    """
    change_report = {}
    for test_dir in get_paths(test_dirs):
        print(f"Testing {test_dir}...")
        report = vcr_create_upload_and_diff(
            test_dir,
            globus_token="offline_test",
            record_mode="none",
            vcr=VCR(serializer="json"),
            dry_run=dry_run,
            verbose=verbose,
        )
        if report:
            change_report[test_dir] = report
    print_change_report(change_report)


def print_change_report(change_report: dict[str, str], verbose: bool = True):
    if change_report:
        print("-------CHANGE REPORT-------")
        if verbose:
            for dir, message in change_report.items():
                print(f"{dir}: {message}")
            # TODO: update readme docs
            print(
                dedent(
                    f"""
                To update all fixture/readme data, run:
                    env PYTHONPATH=src:$PYTHONPATH python -m tests.manual.manual_testing -t {' '.join([str(dir) for dir in change_report.keys()])} -g <globus_token> -o
                """
                )
            )
        else:
            print("Dirs with errors:")
            for dir, _ in change_report.items():
                print(dir)


def get_paths(test_dirs: list[Path]) -> list[Path]:
    dataset_paths = []
    for test_dir in test_dirs:
        # If given top-level path, find all example dirs in subdirs
        if test_dir.absolute() in [Path("examples").absolute()]:
            for dir in parent_dirs:
                sub_dirs = get_sub_dirs(dir)
                for sub_dir in sub_dirs:
                    dataset_paths.append(sub_dir)
            break
        # If given category-level path, find all example dirs
        elif test_dir.absolute() in parent_dirs:
            sub_dirs = get_sub_dirs(test_dir)
            for sub_dir in sub_dirs:
                dataset_paths.append(sub_dir)
        # Otherwise, just add path
        else:
            dataset_paths.append(test_dir)
    return dataset_paths


parent_dirs = [
    Path("examples/dataset-examples").absolute(),
    Path("examples/dataset-iec-examples").absolute(),
    Path("examples/plugin-tests").absolute(),
]


def get_sub_dirs(target_dir: Path) -> list[Path]:
    if target_dir.absolute() in [path.absolute() for path in parent_dirs]:
        sub_dirs = [
            str(example_dir)
            for example_dir in glob(f"{target_dir}/**")
            if Path(example_dir).is_dir()
        ]
        return [Path(dir) for dir in sorted(sub_dirs)]
    return [target_dir]
