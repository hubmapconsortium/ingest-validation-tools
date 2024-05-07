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

CONSTRAINTS_RESPONSE_GOOD = {
    "code": 200,
    "description": [
        {
            "code": 200,
            "description": [
                {"entity_type": "Sample", "sub_type": ["Suspension"], "sub_type_val": None},
                {"entity_type": "Dataset", "sub_type": None, "sub_type_val": None},
            ],
            "name": "OK",
        },
        {
            "code": 200,
            "description": [
                {"entity_type": "Sample", "sub_type": ["Block"], "sub_type_val": None},
                {"entity_type": "Sample", "sub_type": ["Section"], "sub_type_val": None},
                {"entity_type": "Sample", "sub_type": ["Suspension"], "sub_type_val": None},
                {"entity_type": "Dataset", "sub_type": ["Light Sheet"], "sub_type_val": None},
            ],
            "name": "OK",
        },
    ],
    "name": "OK",
}
CONSTRAINTS_RESPONSE_BAD = b'{"code":400,"description":[{"code":200,"description":[{"entity_type":"Sample","sub_type":["Suspension"],"sub_type_val":null},{"entity_type":"Dataset","sub_type":null,"sub_type_val":null}],"name":"OK"},{"code":404,"description":[{"entity_type":"Sample","sub_type":["Block"],"sub_type_val":null},{"entity_type":"Sample","sub_type":["Section"],"sub_type_val":null},{"entity_type":"Sample","sub_type":["Suspension"],"sub_type_val":null},{"entity_type":"Dataset","sub_type":["Light Sheet"],"sub_type_val":null}],"name":"This `Sample` `block` cannot be associated with the provided `ancestors` due to entity constraints. Click the link to view valid entity types that can be `descendants`"}],"name":"Bad Request"}'
