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

SAMPLE_BLOCK_CONSTRAINTS_RESPONSE_BAD = b'{"code":400,"description":[{"code":404,"description":[{"entity_type":"Sample","sub_type":["Suspension"],"sub_type_val":null},{"entity_type":"Dataset","sub_type":null,"sub_type_val":null}],"name":"This `Sample` `section` cannot be associated with the provided `ancestors` due to entity constraints. Click the link to view valid entity types that can be `descendants`"},{"code":200,"description":[{"entity_type":"Sample","sub_type":["Block"],"sub_type_val":null}],"name":"OK"}],"name":"Bad Request"}'

SAMPLE_BLOCK_PARTIAL_CEDAR_RESPONSE_BAD = b'{"schema":{"name":"Sample Block template schema"},"reporting":[{"errorType":"notStandardTerm","column":"processing_time_unit","row":0,"repairSuggestion":"minute","value":"min"},{"errorType":"notStandardTerm","column":"source_storage_duration_unit","row":0,"repairSuggestion":"minute","value":"min"}]}'

SAMPLE_BLOCK_PARTIAL_CEDAR_RESPONSE_GOOD = (
    b'{"schema":{"name":"Sample Block template schema"},"reporting":[]}'
)

SAMPLE_BLOCK_PARTIAL_ENTITY_API_RESPONSE = b'{"entity_type":"sample","sample_category":"block"}'

SAMPLE_ORGAN_PARTIAL_ENTITY_API_RESPONSE = (
    b'{"entity_type":"sample","sample_category":"organ","organ":"RK"}'
)

SAMPLE_SECTION_PARTIAL_ENTITY_API_RESPONSE = (
    b'{"entity_type":"sample","sample_category":"section"}'
)

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
GOOD_DATASET_CONSTRAINTS_RESPONSE = b'{"code":200,"description":[{"code":200,"description":[{"entity_type":"dataset","sub_type":null,"sub_type_val":null},{"entity_type":"Publication","sub_type":null,"sub_type_val":null}],"name":"OK"},{"code":200,"description":[{"entity_type":"dataset","sub_type":null,"sub_type_val":null},{"entity_type":"Publication","sub_type":null,"sub_type_val":null}],"name":"OK"}],"name":"OK"}'

BAD_DATASET_CONSTRAINTS_RESPONSE = b'{"code":400,"description":[{"code":200,"description":[{"entity_type":"dataset","sub_type":null,"sub_type_val":null},{"entity_type":"Publication","sub_type":null,"sub_type_val":null}],"name":"OK"},{"code":404,"description":[{"entity_type":"Sample","sub_type":["Suspension"],"sub_type_val":null}],"name":"This `Sample` `organ` cannot be associated with the provided `ancestors` due to entity constraints. Click the link to view valid entity types that can be `descendants`"}],"name":"Bad Request"}'

TEST_GET_TSV_ERRORS_PARAMS = [
    (
        True,
        SAMPLE_BLOCK_CONSTRAINTS_RESPONSE_GOOD,
        SAMPLE_BLOCK_PARTIAL_CEDAR_RESPONSE_GOOD,
        "./tests/fixtures/sample-block-good.tsv",
        "sample-block",
        [[], []],
    ),
    (
        False,
        SAMPLE_BLOCK_CONSTRAINTS_RESPONSE_BAD,
        SAMPLE_BLOCK_PARTIAL_CEDAR_RESPONSE_BAD,
        "./tests/fixtures/sample-block-bad.tsv",
        "sample-block",
        [
            [
                'On row 2, column "processing_time_unit", value "min" fails because of error "notStandardTerm". Example: minute',
                'On row 2, column "source_storage_duration_unit", value "min" fails because of error "notStandardTerm". Example: minute',
                'On row 2, column "source_id", value "HBM233.CGGG.482" fails because of error "Invalid Ancestor": Invalid ancestor type for TSV type sample/block. Data sent for ancestor HBM233.CGGG.482: sample/section.',
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
                {
                    "column": "source_id",
                    "error": 'value "HBM233.CGGG.482" fails because of error "Invalid Ancestor": Invalid ancestor type for TSV type sample/block. Data sent for ancestor HBM233.CGGG.482: sample/section.',
                    "row": 2,
                },
            ],
        ],
    ),
    (
        False,
        SAMPLE_BLOCK_CONSTRAINTS_RESPONSE_BAD,
        SAMPLE_BLOCK_PARTIAL_CEDAR_RESPONSE_GOOD,
        "./tests/fixtures/sample-block-bad.tsv",
        "sample-block",
        [
            [
                {
                    "column": "source_id",
                    "error": 'value "HBM233.CGGG.482" fails because of error "Invalid Ancestor": Invalid ancestor type for TSV type sample/block. Data sent for ancestor HBM233.CGGG.482: sample/section.',
                    "row": 2,
                }
            ],
            [
                'On row 2, column "source_id", value "HBM233.CGGG.482" fails because of error "Invalid Ancestor": Invalid ancestor type for TSV type sample/block. Data sent for ancestor HBM233.CGGG.482: sample/section.',
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

PLUGIN_DIR_MAP = {
    Path("examples/plugin-tests/expected-failure").absolute(): InfoDict(
        time=None,
        git="WILL_CHANGE",
        dir="examples/plugin-tests/expected-failure/upload",
        tsvs={
            "good-visium-assay-metadata.tsv": {
                "Schema": "visium-no-probes-v2",
                "Metadata schema version": "2",
                "Directory schema version": "visium-no-probes-v2.0",
            },
            "good-visium-histology-metadata.tsv": {
                "Schema": "h-and-e-v2",
                "Metadata schema version": "2",
                "Directory schema version": "visium-no-probes-v2.0",
            },
            "good-visium-rnaseq-metadata.tsv": {
                "Schema": "rnaseq-visium-no-probes-v2",
                "Metadata schema version": "2",
                "Directory schema version": "visium-no-probes-v2.0",
            },
        },
        successful_plugins=["GZValidator"],
    ),
    Path("examples/plugin-tests/prev-gen-codex-expected-failure").absolute(): InfoDict(
        time=None,
        git="WILL_CHANGE",
        dir="examples/plugin-tests/prev-gen-codex-expected-failure/upload",
        tsvs={
            "name-just-needs-to-end-with-metadata.tsv": {
                "Schema": "codex-v1",
                "Metadata schema version": "codex-v1",
                "Directory schema version": "codex-v1.1",
            }
        },
        successful_plugins=["CodexCommonErrorsValidator"],
    ),
}

GOOD_CONTRIBS = [
    {
        "first_name": "Firstname",
        "last_name": "Lastname",
        "middle_name_or_initial": "M.",
        "display_name": "Firstname M. Lastname",
        "affiliation": "College",
        "orcid": "0000-0002-8928-abcd",
        "email": "test@test.com",
        "is_contact": "Yes",
        "is_principal_investigator": "Yes",
        "is_operator": "Yes",
        "metadata_schema_id": "94dae6f8-0756-4ab0-a47b-138e446a9501",
    },
    {
        "first_name": "Firstname2",
        "last_name": "Lastname2",
        "middle_name_or_initial": "M.2",
        "display_name": "Firstname M. Lastname2",
        "affiliation": "College2",
        "orcid": "0000-0002-8928-efgh",
        "email": "test2@test.com",
        "is_contact": "No",
        "is_principal_investigator": "No",
        "is_operator": "No",
        "metadata_schema_id": "94dae6f8-0756-4ab0-a47b-138e446a9501",
    },
]

BAD_CONTRIBS_NO_CONTACT = [
    {
        "first_name": "Firstname",
        "last_name": "Lastname",
        "middle_name_or_initial": "M.",
        "display_name": "Firstname M. Lastname",
        "affiliation": "College",
        "orcid": "0000-0002-8928-abcd",
        "email": "test@test.com",
        "is_contact": "No",
        "is_principal_investigator": "Yes",
        "is_operator": "Yes",
        "metadata_schema_id": "94dae6f8-0756-4ab0-a47b-138e446a9501",
    },
    {
        "first_name": "Firstname2",
        "last_name": "Lastname2",
        "middle_name_or_initial": "M.2",
        "display_name": "Firstname M. Lastname2",
        "affiliation": "College2",
        "orcid": "0000-0002-8928-efgh",
        "email": "test2@test.com",
        "is_contact": "No",
        "is_principal_investigator": "No",
        "is_operator": "No",
        "metadata_schema_id": "94dae6f8-0756-4ab0-a47b-138e446a9501",
    },
]
