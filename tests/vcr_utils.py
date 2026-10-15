from pathlib import Path

from vcr import VCR

from ingest_validation_tools.error_report import ErrorReport
from ingest_validation_tools.upload import Upload
from tests.manual.updaters import UpdateReadme

SHARED_OPTS: dict = {
    "encoding": "ascii",
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


def create_upload(dataset_path: Path, globus_token: str) -> Upload:
    if "dataset-examples" in dataset_path.parts:
        opts = DATASET_EXAMPLES_OPTS
    elif "dataset-iec-examples" in dataset_path.parts:
        opts = DATASET_IEC_EXAMPLES_OPTS
    elif "plugin-tests" in dataset_path.parts:
        opts = PLUGIN_EXAMPLES_OPTS
    else:
        opts = {}
    return Upload(Path(f"{dataset_path}/upload"), globus_token=globus_token, **opts)


def vcr_create_upload_and_diff(
    test_dir: Path,
    globus_token: str,
    record_mode: str,
    verbose: bool = True,
    dry_run: bool = True,
    vcr: VCR | None = None,
) -> str | None:
    my_vcr = vcr or VCR(serializer="json")
    with my_vcr.use_cassette(
        path=test_dir / "fixtures.json",
        record_mode=record_mode,
        decode_compressed_response=True,
        match_on=["body"],
    ):
        upload = create_upload(test_dir, globus_token)
        upload.get_errors()
    updater = UpdateReadme(test_dir, dry_run, verbose, ErrorReport(upload))
    return updater.check_maybe_write_readme()
