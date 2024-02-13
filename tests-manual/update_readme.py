import json
from pathlib import Path
from typing import Dict, Optional

from ingest_validation_tools.error_report import ErrorReport
from ingest_validation_tools.upload import Upload


def update_readme(dir: str, opts: Optional[Dict]):
    if not opts:
        opts = {
            "dataset_ignore_globs": ["ignore-*.tsv", ".*"],
            "upload_ignore_globs": ["drv_ignore_*", "README_ONLINE"],
            "run_plugins": True,
        }
        upload = Upload(Path(f"{dir}/upload"), **opts)
        info = upload.get_info()
        errors = upload.get_errors()
        report = ErrorReport(info=info, errors=errors)
        with open(f"{dir}/README.md", "w") as f:
            f.write(report.as_md())
        with open(f"{dir}/MOCK_RESPONSE.json", "w") as f:
            new_data = {}
            for _, schema in upload.effective_tsv_paths.items():
                new_data[schema.dataset_type] = schema.soft_assay_data
            json.dump(new_data, f)


# TODO: make command line runnable
