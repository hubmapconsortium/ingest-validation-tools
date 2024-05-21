from ingest_validation_tools.enums import DatasetType, OtherTypes
from ingest_validation_tools.schema_loader import (
    AncestorTypeInfo,
    EntityTypeInfo,
    SchemaVersion,
)

SCATACSEQ_HIGHER_VERSION_VALID = {
    "test-schema-v0.0": {
        "files": [
            {
                "pattern": "[^/]+\\.fastq\\.gz",
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
                "pattern": "[^/]+\\.fastq\\.gz",
                "description": "Compressed FastQ file",
                "required": True,
            },
            {
                "pattern": "extras\\/.*",
                "required": False,
                "description": "Folder for general lab-specific files related to the dataset. [Exists in all assays]",
            },
        ]
    },
}

SCATACSEQ_LOWER_VERSION_VALID = {
    "test-schema-v0.0": {
        "files": [
            {
                "pattern": "[^/]+\\.fastq\\.gz",
                "description": "Compressed FastQ file",
                "required": True,
            },
            {
                "pattern": "extras\\/.*",
                "required": False,
                "description": "Folder for general lab-specific files related to the dataset. [Exists in all assays]",
            },
        ]
    },
    "test-schema-v0.1": {
        "files": [
            {
                "pattern": "[^/]+\\.fastq\\.gz",
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
                "pattern": "[^/]+\\.fastq\\.gz",
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
                "pattern": "[^/]+\\.fastq\\.gz",
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

SCATACSEQ_BOTH_VERSIONS_VALID = {
    "test-schema-v0.0": {
        "files": [
            {
                "pattern": "[^/]+\\.fastq\\.gz",
                "description": "Compressed FastQ file",
                "required": True,
            },
            {
                "pattern": "extras\\/.*",
                "required": False,
                "description": "Folder for general lab-specific files related to the dataset. [Exists in all assays]",
            },
        ]
    },
    "test-schema-v0.1": {
        "files": [
            {
                "pattern": "[^/]+\\.fastq\\.gz",
                "description": "Compressed FastQ file",
                "required": True,
            },
            {
                "pattern": "extras\\/.*",
                "required": False,
                "description": "Folder for general lab-specific files related to the dataset. [Exists in all assays]",
            },
        ]
    },
}

SAMPLE_BLOCK_CONSTRAINTS_RESPONSE_GOOD = b'{"code":200,"description":[{"code":200,"description":[{"entity_type":"Sample","sub_type":["Block"],"sub_type_val":null},{"entity_type":"Sample","sub_type":["Section"],"sub_type_val":null},{"entity_type":"Sample","sub_type":["Suspension"],"sub_type_val":null},{"entity_type":"Dataset","sub_type":["Light Sheet"],"sub_type_val":null}],"name":"OK"},{"code":200,"description":[{"entity_type":"Sample","sub_type":["Block"],"sub_type_val":null},{"entity_type":"Sample","sub_type":["Section"],"sub_type_val":null},{"entity_type":"Sample","sub_type":["Suspension"],"sub_type_val":null},{"entity_type":"Dataset","sub_type":["Light Sheet"],"sub_type_val":null}],"name":"OK"}],"name":"OK"}'

SAMPLE_BLOCK_CONSTRAINTS_RESPONSE_BAD = b'{"code":400,"description":[{"code":200,"description":[{"entity_type":"Sample","sub_type":["Block"],"sub_type_val":null},{"entity_type":"Sample","sub_type":["Section"],"sub_type_val":null},{"entity_type":"Sample","sub_type":["Suspension"],"sub_type_val":null},{"entity_type":"Dataset","sub_type":["Light Sheet"],"sub_type_val":null}],"name":"OK"},{"code":404,"description":[{"entity_type":"Sample","sub_type":["Block"],"sub_type_val":null},{"entity_type":"Sample","sub_type":["Section"],"sub_type_val":null},{"entity_type":"Sample","sub_type":["Suspension"],"sub_type_val":null},{"entity_type":"Dataset","sub_type":["Light Sheet"],"sub_type_val":null}],"name":"This `Sample` `block` cannot be associated with the provided `ancestors` due to entity constraints. Click the link to view valid entity types that can be `descendants`"}],"name":"Bad Request"}'

SAMPLE_BLOCK_PARTIAL_CEDAR_RESPONSE_BAD = b'{"schema":{"name":"Sample Block template schema"},"reporting":[{"errorType":"notStandardTerm","column":"processing_time_unit","row":0,"repairSuggestion":"minute","value":"min"},{"errorType":"notStandardTerm","column":"source_storage_duration_unit","row":0,"repairSuggestion":"minute","value":"min"}]}'

SAMPLE_BLOCK_PARTIAL_CEDAR_RESPONSE_GOOD = (
    b'{"schema":{"name":"Sample Block template schema"},"reporting":[]}'
)

SAMPLE_BLOCK_PARTIAL_ENTITY_API_RESPONSE = b'{"entity_type":"sample","sample_category":"block"}'

SAMPLE_ORGAN_PARTIAL_ENTITY_API_RESPONSE = b'{"entity_type":"sample","sample_category":"organ"}'

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
            row=1,
            column="source_id",
        ),
        AncestorTypeInfo(
            entity_type=DatasetType.DATASET,
            entity_sub_type="histology",
            entity_sub_type_val="",
            entity_id="test_id_1",
            source_schema=None,
            row=2,
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
            row=1,
            column="source_id",
        ),
        AncestorTypeInfo(
            entity_type=OtherTypes.SAMPLE,
            entity_sub_type="organ",
            entity_sub_type_val="",
            entity_id="test_id_1",
            source_schema=None,
            row=2,
            column="source_id",
        ),
    ],
)
# Expected payloads from Upload._construct_constraint_check
GOOD_DATASET_EXPECTED_CONSTRAINTS_PAYLOAD = {
    "test_id_0": {
        "ancestors": {"entity_type": "dataset", "sub_type": ["histology"], "sub_type_val": None},
        "descendants": {"entity_type": "dataset", "sub_type": ["histology"], "sub_type_val": None},
    },
    "test_id_1": {
        "ancestors": {"entity_type": "dataset", "sub_type": ["histology"], "sub_type_val": None},
        "descendants": {"entity_type": "dataset", "sub_type": ["histology"], "sub_type_val": None},
    },
}

# bad case: sample/organ cannot be ancestor of dataset
BAD_DATASET_EXPECTED_CONSTRAINTS_PAYLOAD = {
    "test_id_0": {
        "ancestors": {"entity_type": "dataset", "sub_type": ["histology"], "sub_type_val": None},
        "descendants": {"entity_type": "dataset", "sub_type": ["histology"], "sub_type_val": None},
    },
    "test_id_1": {
        "ancestors": {"entity_type": "sample", "sub_type": ["organ"], "sub_type_val": None},
        "descendants": {"entity_type": "dataset", "sub_type": ["histology"], "sub_type_val": None},
    },
}

GOOD_DATASET_CONSTRAINTS_RESPONSE = b'{"code":200,"description":[{"code":200,"description":[{"entity_type":"dataset","sub_type":null,"sub_type_val":null},{"entity_type":"Publication","sub_type":null,"sub_type_val":null}],"name":"OK"},{"code":200,"description":[{"entity_type":"dataset","sub_type":null,"sub_type_val":null},{"entity_type":"Publication","sub_type":null,"sub_type_val":null}],"name":"OK"}],"name":"OK"}'

BAD_DATASET_CONSTRAINTS_RESPONSE = b'{"code":400,"description":[{"code":200,"description":[{"entity_type":"dataset","sub_type":null,"sub_type_val":null},{"entity_type":"Publication","sub_type":null,"sub_type_val":null}],"name":"OK"},{"code":404,"description":[{"entity_type":"Sample","sub_type":["Suspension"],"sub_type_val":null}],"name":"This `Sample` `organ` cannot be associated with the provided `ancestors` due to entity constraints. Click the link to view valid entity types that can be `descendants`"}],"name":"Bad Request"}'

TEST_GET_TSV_ERRORS_PARAMS = [
    (
        True,
        SAMPLE_BLOCK_CONSTRAINTS_RESPONSE_GOOD,
        SAMPLE_BLOCK_PARTIAL_CEDAR_RESPONSE_GOOD,
        "./tests/fixtures/sample-block-good.tsv",
        "sample-block",
        [],
    ),
    (
        False,
        SAMPLE_BLOCK_CONSTRAINTS_RESPONSE_BAD,
        SAMPLE_BLOCK_PARTIAL_CEDAR_RESPONSE_BAD,
        "./tests/fixtures/sample-block-bad.tsv",
        "sample-block",
        [
            'On row 1, column "processing_time_unit", value "min" fails because of error "notStandardTerm". Example: minute',
            'On row 1, column "source_storage_duration_unit", value "min" fails because of error "notStandardTerm". Example: minute',
            "Invalid ancestor type for TSV type sample/block. Data sent for ancestor HBM733.HSZF.798: sample/organ.",
        ],
    ),
    (
        False,
        SAMPLE_BLOCK_CONSTRAINTS_RESPONSE_BAD,
        SAMPLE_BLOCK_PARTIAL_CEDAR_RESPONSE_GOOD,
        "./tests/fixtures/sample-block-bad.tsv",
        "sample-block",
        [
            "Invalid ancestor type for TSV type sample/block. Data sent for ancestor HBM733.HSZF.798: sample/organ.",
        ],
    ),
]

# Expected payloads from Upload._construct_constraint_check
GOOD_DATASET_EXPECTED_PAYLOAD = {
    "test_id_0": {
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
    "test_id_1": {
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
}
# bad case: organ cannot be ancestor of dataset
BAD_DATASET_EXPECTED_PAYLOAD = {
    "test_id_0": {
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
    "test_id_1": {
        "ancestors": {"entity_type": "sample", "sub_type": ["organ"], "sub_type_val": None},
        "descendants": {
            "entity_type": "dataset",
            "sub_type": ["histology"],
            "sub_type_val": None,
        },
    },
}
