from pathlib import Path

from ingest_validation_tools.enums import DatasetType, OtherTypes
from ingest_validation_tools.error_report import InfoDict
from ingest_validation_tools.schema_loader import (
    AncestorTypeInfo,
    EntityTypeInfo,
    SchemaVersion,
)

SCATACSEQ_HIGHER_VERSION_VALID = {
    "test-schema-v0.0": {
        "files": [
            {
                "pattern": ".*\\.fastq\\.gz",
                "description": "Compressed FastQ file",
                "required": True,
            },
            {
                "pattern": ".*extras\\/.*",
                "required": True,
                "description": "Folder for general lab-specific files related to the dataset. [Exists in all assays]",
            },
        ]
    },
    "test-schema-v0.1": {
        "files": [
            {
                "pattern": ".*\\.fastq\\.gz",
                "description": "Compressed FastQ file",
                "required": True,
            },
            {
                "pattern": ".*",
                "description": "other files",
                "required": False,
            },
        ]
    },
}

SCATACSEQ_LOWER_VERSION_VALID = {
    "test-schema-v0.0": {
        "files": [
            {
                "pattern": ".*\\.fastq\\.gz",
                "description": "Compressed FastQ file",
                "required": True,
            },
            {
                "pattern": "extras\\/.*",
                "required": False,
                "description": "Folder for general lab-specific files related to the dataset. [Exists in all assays]",
            },
            {
                "pattern": ".*",
                "description": "other files",
                "required": False,
            },
        ]
    },
    "test-schema-v0.1": {
        "files": [
            {
                "pattern": ".*\\.fastq\\.gz",
                "description": "Compressed FastQ file",
                "required": True,
            },
            {
                "pattern": "extras\\/.*",
                "required": True,
                "description": "Folder for general lab-specific files related to the dataset. [Exists in all assays]",
            },
        ]
    },
}

SCATACSEQ_NEITHER_VERSION_VALID = {
    "test-schema-v0.0": {
        "files": [
            {
                "pattern": ".*\\.fastq\\.gz",
                "description": "Compressed FastQ file",
                "required": True,
            },
            {
                "pattern": "extras\\/.*",
                "required": True,
                "description": "Folder for general lab-specific files related to the dataset. [Exists in all assays]",
            },
        ]
    },
    "test-schema-v0.1": {
        "files": [
            {
                "pattern": ".*\\.fastq\\.gz",
                "description": "Compressed FastQ file",
                "required": True,
            },
            {
                "pattern": "extras\\/.*",
                "required": True,
                "description": "Folder for general lab-specific files related to the dataset. [Exists in all assays]",
            },
        ]
    },
}

SCATACSEQ_BOTH_VERSIONS_VALID: dict[str, dict] = {
    "test-schema-v0.0": {
        "files": [
            {
                "pattern": ".*\\.fastq\\.gz",
                "description": "Compressed FastQ file",
                "required": True,
            },
            {
                "pattern": "extras\\/.*",
                "required": False,
                "description": "Folder for general lab-specific files related to the dataset. [Exists in all assays]",
            },
            {
                "pattern": ".*",
                "description": "other files",
                "required": False,
            },
        ]
    },
    "test-schema-v0.1": {
        "files": [
            {
                "pattern": ".*\\.fastq\\.gz",
                "description": "Compressed FastQ file",
                "required": True,
            },
            {
                "pattern": "extras\\/.*",
                "required": False,
                "description": "Folder for general lab-specific files related to the dataset. [Exists in all assays]",
            },
            {
                "pattern": ".*",
                "description": "other files",
                "required": False,
            },
        ]
    },
}

# ancestor_entities created in Upload._find_and_check_url_fields
# from entity-api responses
# dataset-histology as ancestor of dataset-histology might be gibberish
# but as far as the rules are concerned it is valid
GOOD_DATASET_SCHEMA_WITH_ANCESTORS = SchemaVersion(
    schema_name="histology",
    metadata_type="assays",
    rows=[{"parent_sample_id": "doesn't_matter", "dataset_type": "histology"}],
    entity_type_info=EntityTypeInfo(entity_type=DatasetType.DATASET, entity_sub_type="histology"),
    ancestor_entities=[
        AncestorTypeInfo(
            entity_type=DatasetType.DATASET,
            entity_sub_type="histology",
            entity_sub_type_val="",
            entity_id="test_id_0",
            source_schema=None,
            row=0,
            column="source_id",
        ),
        AncestorTypeInfo(
            entity_type=DatasetType.DATASET,
            entity_sub_type="histology",
            entity_sub_type_val="",
            entity_id="test_id_1",
            source_schema=None,
            row=1,
            column="source_id",
        ),
    ],
)
# bad case: organ cannot be ancestor of dataset
BAD_DATASET_SCHEMA_WITH_ANCESTORS = SchemaVersion(
    schema_name="histology",
    metadata_type="assays",
    rows=[{"parent_sample_id": "doesn't_matter", "dataset_type": "histology"}],
    entity_type_info=EntityTypeInfo(entity_type=DatasetType.DATASET, entity_sub_type="histology"),
    ancestor_entities=[
        AncestorTypeInfo(
            entity_type=DatasetType.DATASET,
            entity_sub_type="histology",
            entity_sub_type_val="",
            entity_id="test_id_0",
            source_schema=None,
            row=0,
            column="source_id",
        ),
        AncestorTypeInfo(
            entity_type=OtherTypes.SAMPLE,
            entity_sub_type="organ",
            entity_sub_type_val="RK",
            entity_id="test_id_1",
            source_schema=None,
            row=1,
            column="source_id",
        ),
    ],
)
TEST_GET_TSV_ERRORS_PARAMS = [
    (
        "./tests/fixtures/sample-block-empty.tsv",
        "sample-block",
        [
            ["File has no data rows: tests/fixtures/sample-block-empty.tsv."],
            [{"error": "File has no data rows: tests/fixtures/sample-block-empty.tsv."}],
        ],
    ),
    (
        "./tests/fixtures/sample-block-bad.tsv",
        "sample-block",
        [
            [
                'On row 2, column "processing_time_unit", value "min" fails because of error "notStandardTerm". Example: minute.',
                'On row 2, column "source_storage_duration_unit", value "min" fails because of error "notStandardTerm". Example: minute.',
            ],
            [
                {
                    "column": "processing_time_unit",
                    "error": 'value "min" fails because of error "notStandardTerm". Example: minute',
                    "row": 2,
                },
                {
                    "column": "source_storage_duration_unit",
                    "error": 'value "min" fails because of error "notStandardTerm". Example: minute',
                    "row": 2,
                },
            ],
        ],
    ),
    (
        "./tests/fixtures/sample-block-bad-no-source.tsv",
        "sample-block",
        [
            [
                {
                    "column": "source_id",
                    "error": 'value "" fails because of error "AssertionError": Unable to check URL for column \'source_id\' on row 2: empty value.',
                    "row": 2,
                },
                {
                    "column": "source_id",
                    "error": 'value "" fails because of error "missingRequired"',
                    "row": 2,
                },
            ],
            [
                'On row 2, column "source_id", value "" fails because of error "AssertionError": Unable to check URL for column "source_id" on row 2: empty value.',
                'On row 2, column "source_id", value "" fails because of error "missingRequired".',
            ],
        ],
    ),
    (
        "./tests/fixtures/contributors_good.tsv",
        "contributors",
        [[], []],
    ),
    (
        "./tests/fixtures/contributors_bad.tsv",
        "contributors",
        [
            [
                {
                    "column": "is_operator",
                    "error": 'value "" fails because of error "missingRequired"',
                    "row": 2,
                },
            ],
            [
                'On row 2, column "is_operator", value "" fails because of error "missingRequired".',
            ],
        ],
    ),
]

# Expected payloads from Upload._construct_constraint_check
GOOD_DATASET_EXPECTED_PAYLOAD = [
    {
        "ancestors": {
            "entity_type": "dataset",
            "sub_type": ["histology"],
            "sub_type_val": None,
        },
        "descendants": {
            "entity_type": "dataset",
            "sub_type": ["histology"],
            "sub_type_val": None,
        },
    },
    {
        "ancestors": {
            "entity_type": "dataset",
            "sub_type": ["histology"],
            "sub_type_val": None,
        },
        "descendants": {
            "entity_type": "dataset",
            "sub_type": ["histology"],
            "sub_type_val": None,
        },
    },
]
# bad case: organ cannot be ancestor of dataset
BAD_DATASET_EXPECTED_PAYLOAD = [
    {
        "ancestors": {
            "entity_type": "dataset",
            "sub_type": ["histology"],
            "sub_type_val": None,
        },
        "descendants": {
            "entity_type": "dataset",
            "sub_type": ["histology"],
            "sub_type_val": None,
        },
    },
    {
        "ancestors": {"entity_type": "sample", "sub_type": ["organ"], "sub_type_val": ["RK"]},
        "descendants": {
            "entity_type": "dataset",
            "sub_type": ["histology"],
            "sub_type_val": None,
        },
    },
]
