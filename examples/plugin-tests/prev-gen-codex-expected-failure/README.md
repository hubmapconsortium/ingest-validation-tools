/home/gesina/code/ingest-validation-tools/examples/plugin-tests/prev-gen-codex-expected-failure/upload/dataset-1/src_something/cycX_regX_X/X_X_ZX_CHX.tif is not a valid TIFF file: not a TIFF file
FOUND dataset.json; skipping further analysis
Threading at 4
Threading at 4
Validating matching fastq files in /home/gesina/code/ingest-validation-tools/examples/plugin-tests/prev-gen-codex-expected-failure/upload/dataset-1
```
Plugin Errors:
  Check CODEX JSON against schema:
  - "/home/gesina/code/ingest-validation-tools/examples/plugin-tests/prev-gen-codex-expected-failure/upload/dataset-1/src_something/dataset.json:\
    \ \"Version\" is a required property\n\nFailed validating \"required\" in schema:\n\
    \    {\"$id\": \"http://example.com/example.json\",\n     \"$schema\": \"http://json-schema.org/draft-07/schema\"\
    ,\n     \"additionalProperties\": True,\n     \"default\": {},\n     \"description\"\
    : \"The root schema comprises the entire JSON document.\",\n     \"examples\"\
    : [{\"AcquisitionDate\": \"2020-02-19T13:51:35.857-05:00[America/New_York]\",\n\
    \                   \"AcquisitionMode\": \"Confocal\",\n                   \"\
    AssaySpecificSoftware\": \"Akoya CODEX Instrument \"\n                       \
    \                     \"Manager 1.29, akoya CODEX \"\n                       \
    \                     \"Processor 1.7.6\",\n                   \"AssayType\":\
    \ \"CODEX\",\n                   \"BitDepth\": 16,\n                   \"ChannelDetails\"\
    : {\"ChannelDetailsArray\": [{\"Binning\": 1,\n                              \
    \                                 \"ChannelID\": 1,\n                        \
    \                                       \"CycleID\": 1,\n                    \
    \                                           \"EmissionWavelengthNM\": 450,\n \
    \                                                              \"ExcitationWavelengthNM\"\
    : 350,\n                                                               \"ExposureTimeMS\"\
    : 10.0,\n                                                               \"Fluorophore\"\
    : \"DAPI\",\n                                                               \"\
    Gain\": 1.0,\n                                                               \"\
    Name\": \"DAPI-01\",\n                                                       \
    \        \"PassedQC\": True,\n                                               \
    \                \"QCDetails\": \"if \"\n                                    \
    \                                        \"QC \"\n                           \
    \                                                 \"failed \"\n              \
    \                                                              \"why\"},\n   \
    \                                                           {\"Binning\": 1,\n\
    \                                                               \"ChannelID\"\
    : 2,\n                                                               \"CycleID\"\
    : 1,\n                                                               \"EmissionWavelengthNM\"\
    : 660,\n                                                               \"ExcitationWavelengthNM\"\
    : 650,\n                                                               \"ExposureTimeMS\"\
    : 100.0,\n                                                               \"Fluorophore\"\
    : \"Cy5\",\n                                                               \"\
    Gain\": 1.0,\n                                                               \"\
    Name\": \"CD31\",\n                                                          \
    \     \"PassedQC\": True,\n                                                  \
    \             \"QCDetails\": \"None\"}]},\n                   \"DatasetName\"\
    : \"Some recognizable name\",\n                   \"ImmersionMedium\": \"Air\"\
    ,\n                   \"MembraneStain\": [{\"ChannelID\": 3, \"CycleID\": 2},\n\
    \                                     {\"ChannelID\": 4, \"CycleID\": 3}],\n \
    \                  \"MembraneStainForSegmentation\": {\"ChannelID\": 4,\n    \
    \                                                \"CycleID\": 3},\n          \
    \         \"Microscope\": \"Sony, nikon, zeiss\",\n                   \"NominalMagnification\"\
    : 40,\n                   \"NuclearStain\": [{\"ChannelID\": 1, \"CycleID\": 2}],\n\
    \                   \"NuclearStainForSegmentation\": {\"ChannelID\": 1,\n    \
    \                                               \"CycleID\": 2},\n           \
    \        \"NumChannels\": 6,\n                   \"NumCycles\": 4,\n         \
    \          \"NumRegions\": 3,\n                   \"NumZPlanes\": 5,\n       \
    \            \"NumericalAperture\": 1.0,\n                   \"RegionHeight\"\
    : 10,\n                   \"RegionWidth\": 10,\n                   \"ResolutionX\"\
    : 300,\n                   \"ResolutionXUnit\": \"nm\",\n                   \"\
    ResolutionY\": 300,\n                   \"ResolutionYUnit\": \"nm\",\n       \
    \            \"ResolutionZ\": 100,\n                   \"ResolutionZUnit\": \"\
    nm\",\n                   \"TileHeight\": 2048,\n                   \"TileLayout\"\
    : \"Snake\",\n                   \"TileOverlapX\": 0.3,\n                   \"\
    TileOverlapY\": 0.3,\n                   \"TileWidth\": 2048,\n              \
    \     \"Version\": \"1.0\"}],\n     \"properties\": {\"AcquisitionDate\": {\"\
    $id\": \"#/properties/AcquisitionDate\",\n                                   \
    \     \"default\": \"None\",\n                                        \"description\"\
    : \"Dataset \"\n                                                       \"acquisition\
    \ date.\",\n                                        \"examples\": [\"2020-02-19T13:51:35.857-05:00[America/New_York]\"\
    ],\n                                        \"title\": \"The AcquisitionDate \"\
    \n                                                 \"schema\",\n             \
    \                           \"type\": \"string\"},\n                    \"AcquisitionMode\"\
    : {\"$id\": \"#/properties/AcquisitionMode\",\n                              \
    \          \"default\": \"Confocal\",\n                                      \
    \  \"description\": \"Type of the \"\n                                       \
    \                \"microscopy method.\",\n                                   \
    \     \"enum\": [\"Confocal\",\n                                             \
    \    \"WideField\",\n                                                 \"Lightsheet\"\
    ,\n                                                 \"SingleMolecule\",\n    \
    \                                             \"MultiPhoton\",\n             \
    \                                    \"StructuredIllumination\",\n           \
    \                                      \"Spectral\",\n                       \
    \                          \"TotalInternalReflection\",\n                    \
    \                             \"BrightField\"],\n                            \
    \            \"examples\": [\"Confocal\"],\n                                 \
    \       \"title\": \"The AcquisitionMode \"\n                                \
    \                 \"schema\",\n                                        \"type\"\
    : \"string\"},\n                    \"AssaySpecificSoftware\": {\"$id\": \"#/properties/AssaySpecificSoftware\"\
    ,\n                                              \"default\": \"None\",\n    \
    \                                          \"description\": \"The comma \"\n \
    \                                                            \"separated \"\n\
    \                                                             \"list of \"\n \
    \                                                            \"company, \"\n \
    \                                                            \"name and \"\n \
    \                                                            \"version of \"\n\
    \                                                             \"the assay \"\n\
    \                                                             \"specific \"\n\
    \                                                             \"software \"\n\
    \                                                             \"used for \"\n\
    \                                                             \"this \"\n    \
    \                                                         \"dataset.\",\n    \
    \                                          \"examples\": [\"Akoya CODEX \"\n \
    \                                                          \"Instrument \"\n \
    \                                                          \"Manager 1.29, \"\n\
    \                                                           \"Akoya CODEX \"\n\
    \                                                           \"Processor \"\n \
    \                                                          \"1.7.6 \"],\n    \
    \                                          \"title\": \"The \"\n             \
    \                                          \"AssaySpecificSoftware \"\n      \
    \                                                 \"schema\",\n              \
    \                                \"type\": \"string\"},\n                    \"\
    AssayType\": {\"$id\": \"#/properties/AssayType\",\n                         \
    \         \"default\": \"None\",\n                                  \"description\"\
    : \"The type of the assay.\",\n                                  \"enum\": [\"\
    CODEX\", \"ImmunoSABER\"],\n                                  \"examples\": [\"\
    CODEX\"],\n                                  \"title\": \"The AssayType schema\"\
    ,\n                                  \"type\": \"string\"},\n                \
    \    \"BitDepth\": {\"$id\": \"#/properties/BitDepth\",\n                    \
    \             \"default\": 16,\n                                 \"description\"\
    : \"Size of the tile \"\n                                                \"horizontal\
    \ direction in \"\n                                                \"pixels of\
    \ bits per pixel.\",\n                                 \"examples\": [16],\n \
    \                                \"multipleOf\": 2,\n                        \
    \         \"title\": \"The BitDepth schema\",\n                              \
    \   \"type\": \"integer\"},\n                    \"ChannelDetails\": {\"$id\"\
    : \"#/properties/ChannelDetails\",\n                                       \"\
    additionalProperties\": True,\n                                       \"default\"\
    : {},\n                                       \"description\": \"The acquisition\
    \ \"\n                                                      \"details for each\
    \ \"\n                                                      \"imaging channel.\"\
    ,\n                                       \"examples\": [{\"ChannelDetailsArray\"\
    : [{\"Binning\": 1,\n                                                        \
    \                      \"ChannelID\": 1,\n                                   \
    \                                           \"CycleID\": 1,\n                \
    \                                                              \"EmissionWavelengthNM\"\
    : 450,\n                                                                     \
    \         \"ExcitationWavelengthNM\": 350,\n                                 \
    \                                             \"ExposureTimeMS\": 10.0,\n    \
    \                                                                          \"\
    Fluorophore\": \"DAPI\",\n                                                   \
    \                           \"Gain\": 1.0,\n                                 \
    \                                             \"Name\": \"DAPI-01\",\n       \
    \                                                                       \"PassedQC\"\
    : True,\n                                                                    \
    \          \"QCDetails\": \"if \"\n                                          \
    \                                                 \"QC \"\n                  \
    \                                                                         \"failed\
    \ \"\n                                                                       \
    \                    \"why\"},\n                                             \
    \                                {\"Binning\": 1,\n                          \
    \                                                    \"ChannelID\": 2,\n     \
    \                                                                         \"CycleID\"\
    : 1,\n                                                                       \
    \       \"EmissionWavelengthNM\": 660,\n                                     \
    \                                         \"ExcitationWavelengthNM\": 650,\n \
    \                                                                            \
    \ \"ExposureTimeMS\": 100.0,\n                                               \
    \                               \"Fluorophore\": \"Cy5\",\n                  \
    \                                                            \"Gain\": 1.0,\n\
    \                                                                            \
    \  \"Name\": \"CD31\",\n                                                     \
    \                         \"PassedQC\": True,\n                              \
    \                                                \"QCDetails\": \"None\"}]}],\n\
    \                                       \"properties\": {\"ChannelDetailsArray\"\
    : {\"$id\": \"#/properties/ChannelDetails/properties/ChannelDetailsArray\",\n\
    \                                                                            \
    \  \"additionalItems\": True,\n                                              \
    \                                \"default\": [],\n                          \
    \                                                    \"description\": \"An \"\n\
    \                                                                            \
    \                 \"explanation \"\n                                         \
    \                                                    \"about \"\n            \
    \                                                                            \
    \     \"the \"\n                                                             \
    \                                \"purpose \"\n                              \
    \                                                               \"of \"\n    \
    \                                                                            \
    \             \"this \"\n                                                    \
    \                                         \"instance.\",\n                   \
    \                                                           \"examples\": [[{\"\
    Binning\": 1,\n                                                              \
    \                               \"ChannelID\": 1,\n                          \
    \                                                                   \"CycleID\"\
    : 1,\n                                                                       \
    \                      \"EmissionWavelengthNM\": 450,\n                      \
    \                                                                       \"ExcitationWavelengthNM\"\
    : 350,\n                                                                     \
    \                        \"ExposureTimeMS\": 10.0,\n                         \
    \                                                                    \"Fluorophore\"\
    : \"DAPI\",\n                                                                \
    \                             \"Gain\": 1.0,\n                               \
    \                                                              \"Name\": \"DAPI-01\"\
    ,\n                                                                          \
    \                   \"PassedQC\": True,\n                                    \
    \                                                         \"QCDetails\": \"if\
    \ \"\n                                                                       \
    \                                   \"QC \"\n                                \
    \                                                                          \"\
    failed \"\n                                                                  \
    \                                        \"why\"},\n                         \
    \                                                                   {\"Binning\"\
    : 1,\n                                                                       \
    \                      \"ChannelID\": 2,\n                                   \
    \                                                          \"CycleID\": 1,\n \
    \                                                                            \
    \                \"EmissionWavelengthNM\": 660,\n                            \
    \                                                                 \"ExcitationWavelengthNM\"\
    : 650,\n                                                                     \
    \                        \"ExposureTimeMS\": 100.0,\n                        \
    \                                                                     \"Fluorophore\"\
    : \"Cy5\",\n                                                                 \
    \                            \"Gain\": 1.0,\n                                \
    \                                                             \"Name\": \"CD31\"\
    ,\n                                                                          \
    \                   \"PassedQC\": True,\n                                    \
    \                                                         \"QCDetails\": \"None\"\
    }]],\n                                                                       \
    \       \"items\": {\"$id\": \"#/properties/ChannelDetails/properties/ChannelDetailsArray/items\"\
    ,\n                                                                          \
    \              \"allOf\": [{\"$id\": \"#/properties/ChannelDetails/properties/ChannelDetailsArray/items/allOf/0\"\
    ,\n                                                                          \
    \                         \"additionalProperties\": True,\n                  \
    \                                                                            \
    \     \"default\": {},\n                                                     \
    \                                              \"description\": \"An \"\n    \
    \                                                                            \
    \                                  \"explanation \"\n                        \
    \                                                                            \
    \              \"about \"\n                                                  \
    \                                                                \"the \"\n  \
    \                                                                            \
    \                                    \"purpose \"\n                          \
    \                                                                            \
    \            \"of \"\n                                                       \
    \                                                           \"this \"\n      \
    \                                                                            \
    \                                \"instance.\",\n                            \
    \                                                                       \"examples\"\
    : [{\"Binning\": 1,\n                                                        \
    \                                                         \"ChannelID\": 1,\n\
    \                                                                            \
    \                                     \"CycleID\": 1,\n                      \
    \                                                                            \
    \               \"EmissionWavelengthNM\": 450,\n                             \
    \                                                                            \
    \        \"ExcitationWavelengthNM\": 350,\n                                  \
    \                                                                            \
    \   \"ExposureTimeMS\": 10.0,\n                                              \
    \                                                                   \"Fluorophore\"\
    : \"DAPI\",\n                                                                \
    \                                                 \"Gain\": 1.0,\n           \
    \                                                                            \
    \                          \"Name\": \"DAPI-01\",\n                          \
    \                                                                            \
    \           \"PassedQC\": True,\n                                            \
    \                                                                     \"QCDetails\"\
    : \"if \"\n                                                                  \
    \                                                            \"QC \"\n       \
    \                                                                            \
    \                                           \"failed \"\n                    \
    \                                                                            \
    \                              \"why\"}],\n                                  \
    \                                                                 \"properties\"\
    : {\"Binning\": {\"$id\": \"#/properties/ChannelDetails/properties/ChannelDetailsArray/items/allOf/0/properties/Binning\"\
    ,\n                                                                          \
    \                                                    \"default\": 1,\n       \
    \                                                                            \
    \                                           \"description\": \"The \"\n      \
    \                                                                            \
    \                                                           \"number \"\n    \
    \                                                                            \
    \                                                             \"of \"\n      \
    \                                                                            \
    \                                                           \"pixels \"\n    \
    \                                                                            \
    \                                                             \"that \"\n    \
    \                                                                            \
    \                                                             \"are \"\n     \
    \                                                                            \
    \                                                            \"combined \"\n \
    \                                                                            \
    \                                                                \"during \"\n\
    \                                                                            \
    \                                                                 \"or \"\n  \
    \                                                                            \
    \                                                               \"after \"\n \
    \                                                                            \
    \                                                                \"detection.\"\
    ,\n                                                                          \
    \                                                    \"examples\": [1],\n    \
    \                                                                            \
    \                                              \"minimum\": 1,\n             \
    \                                                                            \
    \                                     \"title\": \"The \"\n                  \
    \                                                                            \
    \                                         \"Binning \"\n                     \
    \                                                                            \
    \                                      \"schema\",\n                         \
    \                                                                            \
    \                         \"type\": \"integer\"},\n                          \
    \                                                                            \
    \            \"ChannelID\": {\"$id\": \"#/properties/ChannelDetails/properties/ChannelDetailsArray/items/allOf/0/properties/ChannelID\"\
    ,\n                                                                          \
    \                                                      \"default\": 1,\n     \
    \                                                                            \
    \                                               \"description\": \"The \"\n  \
    \                                                                            \
    \                                                                 \"id \"\n  \
    \                                                                            \
    \                                                                 \"of \"\n  \
    \                                                                            \
    \                                                                 \"the \"\n \
    \                                                                            \
    \                                                                  \"imaging \"\
    \n                                                                           \
    \                                                                    \"channel\
    \ \"\n                                                                       \
    \                                                                        \"inside\
    \ \"\n                                                                       \
    \                                                                        \"the\
    \ \"\n                                                                       \
    \                                                                        \"cycle.\"\
    ,\n                                                                          \
    \                                                      \"examples\": [1],\n  \
    \                                                                            \
    \                                                  \"minimum\": 1,\n         \
    \                                                                            \
    \                                           \"title\": \"The \"\n            \
    \                                                                            \
    \                                                 \"ChannelID \"\n           \
    \                                                                            \
    \                                                  \"schema\",\n             \
    \                                                                            \
    \                                       \"type\": \"integer\"},\n            \
    \                                                                            \
    \                          \"CycleID\": {\"$id\": \"#/properties/ChannelDetails/properties/ChannelDetailsArray/items/allOf/0/properties/CycleID\"\
    ,\n                                                                          \
    \                                                    \"default\": 1,\n       \
    \                                                                            \
    \                                           \"description\": \"The \"\n      \
    \                                                                            \
    \                                                           \"id \"\n        \
    \                                                                            \
    \                                                         \"of \"\n          \
    \                                                                            \
    \                                                       \"the \"\n           \
    \                                                                            \
    \                                                      \"imaging \"\n        \
    \                                                                            \
    \                                                         \"cycle.\",\n      \
    \                                                                            \
    \                                            \"examples\": [1],\n            \
    \                                                                            \
    \                                      \"minimum\": 1,\n                     \
    \                                                                            \
    \                             \"title\": \"The \"\n                          \
    \                                                                            \
    \                                 \"CycleID \"\n                             \
    \                                                                            \
    \                              \"schema\",\n                                 \
    \                                                                            \
    \                 \"type\": \"integer\"},\n                                  \
    \                                                                            \
    \    \"EmissionWavelengthNM\": {\"$id\": \"#/properties/ChannelDetails/properties/ChannelDetailsArray/items/allOf/0/properties/EmissionWavelengthNM\"\
    ,\n                                                                          \
    \                                                                 \"default\"\
    : 1,\n                                                                       \
    \                                                                    \"description\"\
    : \"The \"\n                                                                 \
    \                                                                            \
    \             \"wavelength \"\n                                              \
    \                                                                            \
    \                                \"of \"\n                                   \
    \                                                                            \
    \                                           \"light \"\n                     \
    \                                                                            \
    \                                                         \"emission \"\n    \
    \                                                                            \
    \                                                                          \"\
    by \"\n                                                                      \
    \                                                                            \
    \        \"a \"\n                                                            \
    \                                                                            \
    \                  \"fluorophore \"\n                                        \
    \                                                                            \
    \                                      \"in \"\n                             \
    \                                                                            \
    \                                                 \"nanometers.\",\n         \
    \                                                                            \
    \                                                      \"examples\": [450],\n\
    \                                                                            \
    \                                                               \"minimum\": 1,\n\
    \                                                                            \
    \                                                               \"title\": \"\
    The \"\n                                                                     \
    \                                                                            \
    \   \"EmissionWavelengthNM \"\n                                              \
    \                                                                            \
    \                          \"schema\",\n                                     \
    \                                                                            \
    \                          \"type\": \"integer\"},\n                         \
    \                                                                            \
    \             \"ExcitationWavelengthNM\": {\"$id\": \"#/properties/ChannelDetails/properties/ChannelDetailsArray/items/allOf/0/properties/ExcitationWavelengthNM\"\
    ,\n                                                                          \
    \                                                                   \"default\"\
    : 1,\n                                                                       \
    \                                                                      \"description\"\
    : \"The \"\n                                                                 \
    \                                                                            \
    \               \"wavelength \"\n                                            \
    \                                                                            \
    \                                    \"of \"\n                               \
    \                                                                            \
    \                                                 \"light \"\n               \
    \                                                                            \
    \                                                                 \"absorption\
    \ \"\n                                                                       \
    \                                                                            \
    \         \"by \"\n                                                          \
    \                                                                            \
    \                      \"a \"\n                                              \
    \                                                                            \
    \                                  \"fluorophore \"\n                        \
    \                                                                            \
    \                                                        \"in \"\n           \
    \                                                                            \
    \                                                                     \"nanometers.\"\
    ,\n                                                                          \
    \                                                                   \"examples\"\
    : [350],\n                                                                   \
    \                                                                          \"\
    minimum\": 1,\n                                                              \
    \                                                                            \
    \   \"title\": \"The \"\n                                                    \
    \                                                                            \
    \                      \"ExcitationWavelengthNM \"\n                         \
    \                                                                            \
    \                                                 \"schema\",\n              \
    \                                                                            \
    \                                                   \"type\": \"integer\"},\n\
    \                                                                            \
    \                                      \"ExposureTimeMS\": {\"$id\": \"#/properties/ChannelDetails/properties/ChannelDetailsArray/items/allOf/0/properties/ExposureTimeMS\"\
    ,\n                                                                          \
    \                                                           \"default\": 0.0,\n\
    \                                                                            \
    \                                                         \"description\": \"\
    The \"\n                                                                     \
    \                                                                            \
    \   \"length \"\n                                                            \
    \                                                                            \
    \            \"of \"\n                                                       \
    \                                                                            \
    \                 \"the \"\n                                                 \
    \                                                                            \
    \                       \"exposure \"\n                                      \
    \                                                                            \
    \                                  \"in \"\n                                 \
    \                                                                            \
    \                                       \"milliseconds.\",\n                 \
    \                                                                            \
    \                                        \"examples\": [10.0],\n             \
    \                                                                            \
    \                                            \"minimum\": 0.0,\n             \
    \                                                                            \
    \                                            \"title\": \"The \"\n           \
    \                                                                            \
    \                                                       \"ExposureTimeMS \"\n\
    \                                                                            \
    \                                                                  \"schema\"\
    ,\n                                                                          \
    \                                                           \"type\": \"number\"\
    },\n                                                                         \
    \                                         \"Fluorophore\": {\"$id\": \"#/properties/ChannelDetails/properties/ChannelDetailsArray/items/allOf/0/properties/Fluorophore\"\
    ,\n                                                                          \
    \                                                        \"default\": \"None\"\
    ,\n                                                                          \
    \                                                        \"description\": \"The\
    \ \"\n                                                                       \
    \                                                                          \"\
    name \"\n                                                                    \
    \                                                                            \
    \ \"of \"\n                                                                  \
    \                                                                            \
    \   \"the \"\n                                                               \
    \                                                                            \
    \      \"fluorophore \"\n                                                    \
    \                                                                            \
    \                 \"for \"\n                                                 \
    \                                                                            \
    \                    \"this \"\n                                             \
    \                                                                            \
    \                        \"channel.\",\n                                     \
    \                                                                            \
    \                 \"examples\": [\"DAPI\"],\n                                \
    \                                                                            \
    \                      \"title\": \"The \"\n                                 \
    \                                                                            \
    \                              \"Fluorophore \"\n                            \
    \                                                                            \
    \                                   \"schema\",\n                            \
    \                                                                            \
    \                          \"type\": \"string\"},\n                          \
    \                                                                            \
    \            \"Gain\": {\"$id\": \"#/properties/ChannelDetails/properties/ChannelDetailsArray/items/allOf/0/properties/Gain\"\
    ,\n                                                                          \
    \                                                 \"default\": 1.0,\n        \
    \                                                                            \
    \                                       \"description\": \"Amplification \"\n\
    \                                                                            \
    \                                                              \"applied \"\n\
    \                                                                            \
    \                                                              \"to \"\n     \
    \                                                                            \
    \                                                         \"the \"\n         \
    \                                                                            \
    \                                                     \"detector \"\n        \
    \                                                                            \
    \                                                      \"signal.\",\n        \
    \                                                                            \
    \                                       \"examples\": [1.0],\n               \
    \                                                                            \
    \                                \"minimum\": 1.0,\n                         \
    \                                                                            \
    \                      \"title\": \"The \"\n                                 \
    \                                                                            \
    \                       \"Gain \"\n                                          \
    \                                                                            \
    \              \"schema\",\n                                                 \
    \                                                                          \"\
    type\": \"number\"},\n                                                       \
    \                                                           \"Name\": {\"$id\"\
    : \"#/properties/ChannelDetails/properties/ChannelDetailsArray/items/allOf/0/properties/Name\"\
    ,\n                                                                          \
    \                                                 \"default\": \"None\",\n   \
    \                                                                            \
    \                                            \"description\": \"The \"\n     \
    \                                                                            \
    \                                                         \"name \"\n        \
    \                                                                            \
    \                                                      \"of \"\n             \
    \                                                                            \
    \                                                 \"the \"\n                 \
    \                                                                            \
    \                                             \"channel \"\n                 \
    \                                                                            \
    \                                             \"or \"\n                      \
    \                                                                            \
    \                                        \"its \"\n                          \
    \                                                                            \
    \                                    \"target.\",\n                          \
    \                                                                            \
    \                     \"examples\": [\"DAPI-01\"],\n                         \
    \                                                                            \
    \                      \"title\": \"The \"\n                                 \
    \                                                                            \
    \                       \"Name \"\n                                          \
    \                                                                            \
    \              \"schema\",\n                                                 \
    \                                                                          \"\
    type\": \"string\"},\n                                                       \
    \                                                           \"PassedQC\": {\"\
    $id\": \"#/properties/ChannelDetails/properties/ChannelDetailsArray/items/allOf/0/properties/PassedQC\"\
    ,\n                                                                          \
    \                                                     \"default\": True,\n   \
    \                                                                            \
    \                                                \"description\": \"Check \"\n\
    \                                                                            \
    \                                                                  \"if \"\n \
    \                                                                            \
    \                                                                 \"the \"\n \
    \                                                                            \
    \                                                                 \"channel \"\
    \n                                                                           \
    \                                                                   \"passed \"\
    \n                                                                           \
    \                                                                   \"qc.\",\n\
    \                                                                            \
    \                                                   \"examples\": [True],\n  \
    \                                                                            \
    \                                                 \"title\": \"The \"\n      \
    \                                                                            \
    \                                                      \"PassedQC \"\n       \
    \                                                                            \
    \                                                     \"schema\",\n          \
    \                                                                            \
    \                                         \"type\": \"boolean\"},\n          \
    \                                                                            \
    \                            \"QCDetails\": {\"$id\": \"#/properties/ChannelDetails/properties/ChannelDetailsArray/items/allOf/0/properties/QCDetails\"\
    ,\n                                                                          \
    \                                                      \"default\": \"None\",\n\
    \                                                                            \
    \                                                    \"description\": \"Additional\
    \ \"\n                                                                       \
    \                                                                        \"details\
    \ \"\n                                                                       \
    \                                                                        \"about\
    \ \"\n                                                                       \
    \                                                                        \"qc.\"\
    ,\n                                                                          \
    \                                                      \"examples\": [\"if \"\n\
    \                                                                            \
    \                                                                 \"QC \"\n  \
    \                                                                            \
    \                                                               \"failed \"\n\
    \                                                                            \
    \                                                                 \"why\"],\n\
    \                                                                            \
    \                                                    \"title\": \"The \"\n   \
    \                                                                            \
    \                                                          \"QCDetails \"\n  \
    \                                                                            \
    \                                                           \"schema\",\n    \
    \                                                                            \
    \                                                \"type\": \"string\"}},\n   \
    \                                                                            \
    \                    \"required\": [\"Name\",\n                              \
    \                                                                            \
    \      \"ChannelID\",\n                                                      \
    \                                                          \"CycleID\",\n    \
    \                                                                            \
    \                                \"PassedQC\",\n                             \
    \                                                                            \
    \       \"ExposureTimeMS\",\n                                                \
    \                                                                \"EmissionWavelengthNM\"\
    ],\n                                                                         \
    \                          \"title\": \"The \"\n                             \
    \                                                                            \
    \   \"first \"\n                                                             \
    \                                               \"allOf \"\n                 \
    \                                                                            \
    \               \"schema\",\n                                                \
    \                                                   \"type\": \"object\"}]},\n\
    \                                                                            \
    \  \"minItems\": 1,\n                                                        \
    \                      \"title\": \"The \"\n                                 \
    \                                                      \"ChannelDetailsArray \"\
    \n                                                                           \
    \            \"schema\",\n                                                   \
    \                           \"type\": \"array\",\n                           \
    \                                                   \"uniqueItems\": True}},\n\
    \                                       \"required\": [\"ChannelDetailsArray\"\
    ],\n                                       \"title\": \"The ChannelDetails schema\"\
    ,\n                                       \"type\": \"object\"},\n           \
    \         \"DatasetName\": {\"$id\": \"#/properties/DatasetName\",\n         \
    \                           \"default\": \"None\",\n                         \
    \           \"description\": \"Name of the CODEX \"\n                        \
    \                           \"dataset recognizable \"\n                      \
    \                             \"by the data provider.\",\n                   \
    \                 \"examples\": [\"Some recognizable name\"],\n              \
    \                      \"title\": \"The DatasetName schema\",\n              \
    \                      \"type\": \"string\"},\n                    \"ImmersionMedium\"\
    : {\"$id\": \"#/properties/ImmersionMedium\",\n                              \
    \          \"default\": \"Air\",\n                                        \"description\"\
    : \"Type of the \"\n                                                       \"\
    objective \"\n                                                       \"immersion\
    \ medium.\",\n                                        \"enum\": [\"Air\",\n  \
    \                                               \"Water\",\n                 \
    \                                \"Oil\",\n                                  \
    \               \"Glycerin\"],\n                                        \"examples\"\
    : [\"Air\"],\n                                        \"title\": \"The ImmersionMedium\
    \ \"\n                                                 \"schema\",\n         \
    \                               \"type\": \"string\"},\n                    \"\
    MembraneStain\": {\"$id\": \"#/properties/MembraneStain\",\n                 \
    \                     \"additionalItems\": True,\n                           \
    \           \"default\": [],\n                                      \"description\"\
    : \"A list of cycle and \"\n                                                 \
    \    \"channel ids that \"\n                                                 \
    \    \"capture stained cell \"\n                                             \
    \        \"membranes.\",\n                                      \"examples\":\
    \ [[{\"ChannelID\": 3,\n                                                     \"\
    CycleID\": 2},\n                                                    {\"ChannelID\"\
    : 4,\n                                                     \"CycleID\": 3}]],\n\
    \                                      \"items\": {\"$id\": \"#/properties/MembraneStain/items\"\
    ,\n                                                \"allOf\": [{\"$id\": \"#/properties/MembraneStain/items/allOf/0\"\
    ,\n                                                           \"additionalProperties\"\
    : True,\n                                                           \"default\"\
    : {},\n                                                           \"description\"\
    : \"The \"\n                                                                 \
    \         \"cycle \"\n                                                       \
    \                   \"and \"\n                                               \
    \                           \"channel \"\n                                   \
    \                                       \"ids \"\n                           \
    \                                               \"that \"\n                  \
    \                                                        \"capture \"\n      \
    \                                                                    \"stained\
    \ \"\n                                                                       \
    \   \"cell \"\n                                                              \
    \            \"membranes.\",\n                                               \
    \            \"examples\": [{\"ChannelID\": 3,\n                             \
    \                                            \"CycleID\": 2}],\n             \
    \                                              \"properties\": {\"ChannelID\"\
    : {\"$id\": \"#/properties/MembraneStain/items/allOf/0/properties/ChannelID\"\
    ,\n                                                                          \
    \              \"default\": 1,\n                                             \
    \                                           \"description\": \"The \"\n      \
    \                                                                            \
    \                     \"id \"\n                                              \
    \                                                         \"of \"\n          \
    \                                                                            \
    \                 \"the \"\n                                                 \
    \                                                      \"channel \"\n        \
    \                                                                            \
    \                   \"that \"\n                                              \
    \                                                         \"captures \"\n    \
    \                                                                            \
    \                       \"stained \"\n                                       \
    \                                                                \"cell \"\n \
    \                                                                            \
    \                          \"membranes.\",\n                                 \
    \                                                       \"examples\": [3],\n \
    \                                                                            \
    \           \"minimum\": 1,\n                                                \
    \                                        \"title\": \"The \"\n               \
    \                                                                            \
    \      \"Channel \"\n                                                        \
    \                                         \"schema\",\n                      \
    \                                                                  \"type\": \"\
    integer\"},\n                                                                \
    \          \"CycleID\": {\"$id\": \"#/properties/MembraneStain/items/allOf/0/properties/CycleID\"\
    ,\n                                                                          \
    \            \"default\": 1,\n                                               \
    \                                       \"description\": \"The \"\n          \
    \                                                                            \
    \               \"id \"\n                                                    \
    \                                                 \"of \"\n                  \
    \                                                                            \
    \       \"the \"\n                                                           \
    \                                          \"cycle \"\n                      \
    \                                                                            \
    \   \"that \"\n                                                              \
    \                                       \"captures \"\n                      \
    \                                                                            \
    \   \"stained \"\n                                                           \
    \                                          \"cell \"\n                       \
    \                                                                            \
    \  \"membranes.\",\n                                                         \
    \                             \"examples\": [2],\n                           \
    \                                                           \"minimum\": 1,\n\
    \                                                                            \
    \          \"title\": \"The \"\n                                             \
    \                                                  \"Cycle \"\n              \
    \                                                                            \
    \     \"schema\",\n                                                          \
    \                            \"type\": \"integer\"}},\n                      \
    \                                     \"required\": [\"CycleID\",\n          \
    \                                                              \"ChannelID\"],\n\
    \                                                           \"title\": \"The \"\
    \n                                                                    \"first\
    \ \"\n                                                                    \"allOf\
    \ \"\n                                                                    \"schema\"\
    ,\n                                                           \"type\": \"object\"\
    }]},\n                                      \"minItems\": 1,\n               \
    \                       \"title\": \"The MembraneStain schema\",\n           \
    \                           \"type\": \"array\",\n                           \
    \           \"uniqueItems\": True},\n                    \"MembraneStainForSegmentation\"\
    : {\"$id\": \"#/properties/MembraneStainForSegmentation\",\n                 \
    \                                    \"additionalProperties\": True,\n       \
    \                                              \"default\": {},\n            \
    \                                         \"description\": \"The \"\n        \
    \                                                            \"cycle \"\n    \
    \                                                                \"and \"\n  \
    \                                                                  \"channel \"\
    \n                                                                    \"ids \"\
    \n                                                                    \"that \"\
    \n                                                                    \"will \"\
    \n                                                                    \"be \"\n\
    \                                                                    \"used \"\
    \n                                                                    \"for \"\
    \n                                                                    \"cell \"\
    \n                                                                    \"segmentation.\"\
    ,\n                                                     \"examples\": [{\"ChannelID\"\
    : 4,\n                                                                   \"CycleID\"\
    : 3}],\n                                                     \"properties\": {\"\
    ChannelID\": {\"$id\": \"#/properties/MembraneStainForSegmentation/properties/ChannelID\"\
    ,\n                                                                          \
    \        \"default\": 1,\n                                                   \
    \                               \"description\": \"The \"\n                  \
    \                                                                            \
    \   \"channel \"\n                                                           \
    \                                      \"id, \"\n                            \
    \                                                                     \"inside\
    \ \"\n                                                                       \
    \                          \"the \"\n                                        \
    \                                                         \"cycle, \"\n      \
    \                                                                            \
    \               \"that \"\n                                                  \
    \                                               \"will \"\n                  \
    \                                                                            \
    \   \"be \"\n                                                                \
    \                                 \"used \"\n                                \
    \                                                                 \"for \"\n \
    \                                                                            \
    \                    \"cell \"\n                                             \
    \                                                    \"segmentation.\",\n    \
    \                                                                            \
    \  \"examples\": [4],\n                                                      \
    \                            \"minimum\": 1,\n                               \
    \                                                   \"title\": \"The \"\n    \
    \                                                                            \
    \           \"Channel \"\n                                                   \
    \                                        \"schema\",\n                       \
    \                                                           \"type\": \"integer\"\
    },\n                                                                    \"CycleID\"\
    : {\"$id\": \"#/properties/MembraneStainForSegmentation/properties/CycleID\",\n\
    \                                                                            \
    \    \"default\": 1,\n                                                       \
    \                         \"description\": \"The \"\n                        \
    \                                                                       \"cycle\
    \ \"\n                                                                       \
    \                        \"id \"\n                                           \
    \                                                    \"that \"\n             \
    \                                                                            \
    \      \"will \"\n                                                           \
    \                                    \"be \"\n                               \
    \                                                                \"used \"\n \
    \                                                                            \
    \                  \"for \"\n                                                \
    \                                               \"cell \"\n                  \
    \                                                                            \
    \ \"segmentation.\",\n                                                       \
    \                         \"examples\": [3],\n                               \
    \                                                 \"minimum\": 1,\n          \
    \                                                                      \"title\"\
    : \"The \"\n                                                                 \
    \                        \"Cycle \"\n                                        \
    \                                                 \"schema\",\n              \
    \                                                                  \"type\": \"\
    integer\"}},\n                                                     \"required\"\
    : [\"CycleID\",\n                                                            \
    \      \"ChannelID\"],\n                                                     \"\
    title\": \"The \"\n                                                          \
    \    \"MembraneStainForSegmentation \"\n                                     \
    \                         \"schema\",\n                                      \
    \               \"type\": \"object\"},\n                    \"Microscope\": {\"\
    $id\": \"#/properties/Microscope\",\n                                   \"default\"\
    : \"None\",\n                                   \"description\": \"Details about\
    \ the \"\n                                                  \"microscope manufacturer\
    \ \"\n                                                  \"and the model.\",\n\
    \                                   \"examples\": [\"Sony, nikon, zeiss\"],\n\
    \                                   \"title\": \"The Microscope schema\",\n  \
    \                                 \"type\": \"string\"},\n                   \
    \ \"NominalMagnification\": {\"$id\": \"#/properties/NominalMagnification\",\n\
    \                                             \"default\": 40,\n             \
    \                                \"description\": \"The \"\n                 \
    \                                           \"magnification \"\n             \
    \                                               \"of the \"\n                \
    \                                            \"objective as \"\n             \
    \                                               \"specified by \"\n          \
    \                                                  \"the \"\n                \
    \                                            \"manufacturer.\",\n            \
    \                                 \"examples\": [40],\n                      \
    \                       \"minimum\": 0.0,\n                                  \
    \           \"title\": \"The \"\n                                            \
    \          \"NominalMagnification \"\n                                       \
    \               \"schema\",\n                                             \"type\"\
    : \"number\"},\n                    \"NuclearStain\": {\"$id\": \"#/properties/NuclearStain\"\
    ,\n                                     \"additionalItems\": True,\n         \
    \                            \"default\": [],\n                              \
    \       \"description\": \"A list of cycle and \"\n                          \
    \                          \"channel ids that \"\n                           \
    \                         \"capture stained \"\n                             \
    \                       \"nuclei.\",\n                                     \"\
    examples\": [[{\"ChannelID\": 1,\n                                           \
    \         \"CycleID\": 1}]],\n                                     \"items\":\
    \ {\"$id\": \"#/properties/NuclearStain/items\",\n                           \
    \                    \"allOf\": [{\"$id\": \"#/properties/NuclearStain/items/allOf/0\"\
    ,\n                                                          \"additionalProperties\"\
    : True,\n                                                          \"default\"\
    : {},\n                                                          \"description\"\
    : \"The \"\n                                                                 \
    \        \"cycle \"\n                                                        \
    \                 \"and \"\n                                                 \
    \                        \"channel \"\n                                      \
    \                                   \"ids \"\n                               \
    \                                          \"that \"\n                       \
    \                                                  \"capture \"\n            \
    \                                                             \"stained \"\n \
    \                                                                        \"nuclei.\"\
    ,\n                                                          \"examples\": [{\"\
    ChannelID\": 1,\n                                                            \
    \            \"CycleID\": 1}],\n                                             \
    \             \"properties\": {\"ChannelID\": {\"$id\": \"#/properties/NuclearStain/items/allOf/0/properties/ChannelID\"\
    ,\n                                                                          \
    \             \"default\": 1,\n                                              \
    \                                         \"description\": \"The \"\n        \
    \                                                                            \
    \                  \"id \"\n                                                 \
    \                                                     \"of \"\n              \
    \                                                                            \
    \            \"the \"\n                                                      \
    \                                                \"channel, \"\n             \
    \                                                                            \
    \             \"inside \"\n                                                  \
    \                                                    \"the \"\n              \
    \                                                                            \
    \            \"cycle, \"\n                                                   \
    \                                                   \"that \"\n              \
    \                                                                            \
    \            \"captures \"\n                                                 \
    \                                                     \"stained \"\n         \
    \                                                                            \
    \                 \"nuclei.\",\n                                             \
    \                                          \"examples\": [1],\n              \
    \                                                                         \"minimum\"\
    : 1,\n                                                                       \
    \                \"title\": \"The \"\n                                       \
    \                                                         \"Channel \"\n     \
    \                                                                            \
    \               \"schema\",\n                                                \
    \                                       \"type\": \"integer\"},\n            \
    \                                                             \"CycleID\": {\"\
    $id\": \"#/properties/NuclearStain/items/allOf/0/properties/CycleID\",\n     \
    \                                                                            \
    \    \"default\": 1,\n                                                       \
    \                              \"description\": \"The \"\n                   \
    \                                                                            \
    \     \"id \"\n                                                              \
    \                                      \"of \"\n                             \
    \                                                                       \"the\
    \ \"\n                                                                       \
    \                             \"cycle \"\n                                   \
    \                                                                 \"from \"\n\
    \                                                                            \
    \                        \"which \"\n                                        \
    \                                                            \"to \"\n       \
    \                                                                            \
    \                 \"use \"\n                                                 \
    \                                                   \"nuclear \"\n           \
    \                                                                            \
    \             \"stain.\",\n                                                  \
    \                                   \"examples\": [1],\n                     \
    \                                                                \"minimum\":\
    \ 1,\n                                                                       \
    \              \"title\": \"The \"\n                                         \
    \                                                     \"Cycle \"\n           \
    \                                                                            \
    \       \"schema\",\n                                                        \
    \                             \"type\": \"integer\"}},\n                     \
    \                                     \"required\": [\"CycleID\",\n          \
    \                                                             \"ChannelID\"],\n\
    \                                                          \"title\": \"The \"\
    \n                                                                   \"first \"\
    \n                                                                   \"allOf \"\
    \n                                                                   \"schema\"\
    ,\n                                                          \"type\": \"object\"\
    }]},\n                                     \"minItems\": 1,\n                \
    \                     \"title\": \"The NuclearStain schema\",\n              \
    \                       \"type\": \"array\",\n                               \
    \      \"uniqueItems\": True},\n                    \"NuclearStainForSegmentation\"\
    : {\"$id\": \"#/properties/NuclearStainForSegmentation\",\n                  \
    \                                  \"additionalProperties\": True,\n         \
    \                                           \"default\": {},\n               \
    \                                     \"description\": \"The \"\n            \
    \                                                       \"cycle \"\n         \
    \                                                          \"and \"\n        \
    \                                                           \"channel \"\n   \
    \                                                                \"ids \"\n  \
    \                                                                 \"that \"\n\
    \                                                                   \"will \"\n\
    \                                                                   \"be \"\n\
    \                                                                   \"used \"\n\
    \                                                                   \"for \"\n\
    \                                                                   \"nuclear\
    \ \"\n                                                                   \"segmentation.\"\
    ,\n                                                    \"examples\": [{\"ChannelID\"\
    : 1,\n                                                                  \"CycleID\"\
    : 2}],\n                                                    \"properties\": {\"\
    ChannelID\": {\"$id\": \"#/properties/NuclearStainForSegmentation/properties/ChannelID\"\
    ,\n                                                                          \
    \       \"default\": 1,\n                                                    \
    \                             \"description\": \"The \"\n                    \
    \                                                                            \"\
    channel \"\n                                                                 \
    \                               \"id, \"\n                                   \
    \                                                             \"inside \"\n  \
    \                                                                            \
    \                  \"the \"\n                                                \
    \                                                \"cycle, \"\n               \
    \                                                                            \
    \     \"that \"\n                                                            \
    \                                    \"will \"\n                             \
    \                                                                   \"be \"\n\
    \                                                                            \
    \                    \"used \"\n                                             \
    \                                                   \"for \"\n               \
    \                                                                            \
    \     \"nuclear \"\n                                                         \
    \                                       \"segmentation.\",\n                 \
    \                                                                \"examples\"\
    : [1],\n                                                                     \
    \            \"minimum\": 1,\n                                               \
    \                                  \"title\": \"The \"\n                     \
    \                                                                     \"Channel\
    \ \"\n                                                                       \
    \                   \"schema\",\n                                            \
    \                                     \"type\": \"integer\"},\n              \
    \                                                     \"CycleID\": {\"$id\": \"\
    #/properties/NuclearStainForSegmentation/properties/CycleID\",\n             \
    \                                                                  \"default\"\
    : 1,\n                                                                       \
    \        \"description\": \"The \"\n                                         \
    \                                                     \"cycle \"\n           \
    \                                                                            \
    \       \"id \"\n                                                            \
    \                                  \"that \"\n                               \
    \                                                               \"will \"\n  \
    \                                                                            \
    \                \"be \"\n                                                   \
    \                                           \"used \"\n                      \
    \                                                                        \"for\
    \ \"\n                                                                       \
    \                       \"nuclear \"\n                                       \
    \                                                       \"segmentation.\",\n \
    \                                                                            \
    \  \"examples\": [2],\n                                                      \
    \                         \"minimum\": 1,\n                                  \
    \                                             \"title\": \"The \"\n          \
    \                                                                            \
    \  \"Cycle \"\n                                                              \
    \                          \"schema\",\n                                     \
    \                                          \"type\": \"integer\"}},\n        \
    \                                            \"required\": [\"CycleID\",\n   \
    \                                                              \"ChannelID\"],\n\
    \                                                    \"title\": \"The \"\n   \
    \                                                          \"NuclearStainForSegmentation\
    \ \"\n                                                             \"schema\"\
    ,\n                                                    \"type\": \"object\"},\n\
    \                    \"NumChannels\": {\"$id\": \"#/properties/NumChannels\",\n\
    \                                    \"default\": 1,\n                       \
    \             \"description\": \"The number of imaging \"\n                  \
    \                                 \"channels captured.\",\n                  \
    \                  \"examples\": [6],\n                                    \"\
    minimum\": 1,\n                                    \"title\": \"The NumChannels\
    \ schema\",\n                                    \"type\": \"integer\"},\n   \
    \                 \"NumCycles\": {\"$id\": \"#/properties/NumCycles\",\n     \
    \                             \"default\": 1,\n                              \
    \    \"description\": \"The number of cycles in \"\n                         \
    \                        \"the dataset.\",\n                                 \
    \ \"examples\": [4],\n                                  \"minimum\": 1,\n    \
    \                              \"title\": \"The NumCycles schema\",\n        \
    \                          \"type\": \"integer\"},\n                    \"NumRegions\"\
    : {\"$id\": \"#/properties/NumRegions\",\n                                   \"\
    default\": 1,\n                                   \"description\": \"The number\
    \ of regions \"\n                                                  \"in the dataset.\"\
    ,\n                                   \"examples\": [3],\n                   \
    \                \"minimum\": 1,\n                                   \"title\"\
    : \"The NumRegions schema\",\n                                   \"type\": \"\
    integer\"},\n                    \"NumZPlanes\": {\"$id\": \"#/properties/NumZPlanes\"\
    ,\n                                   \"default\": 1,\n                      \
    \             \"description\": \"The number of focal \"\n                    \
    \                              \"planes captured.\",\n                       \
    \            \"examples\": [5],\n                                   \"minimum\"\
    : 1,\n                                   \"title\": \"The NumZPlanes schema\"\
    ,\n                                   \"type\": \"integer\"},\n              \
    \      \"NumericalAperture\": {\"$id\": \"#/properties/NumericalAperture\",\n\
    \                                          \"default\": 0.1,\n               \
    \                           \"description\": \"The numerical \"\n            \
    \                                             \"aperture of the \"\n         \
    \                                                \"objective.\",\n           \
    \                               \"examples\": [1.0],\n                       \
    \                   \"minimum\": 0.1,\n                                      \
    \    \"title\": \"The NumericalAperture \"\n                                 \
    \                  \"schema\",\n                                          \"type\"\
    : \"number\"},\n                    \"RegionHeight\": {\"$id\": \"#/properties/RegionHeight\"\
    ,\n                                     \"default\": 1,\n                    \
    \                 \"description\": \"The number of tiles \"\n                \
    \                                    \"per region in \"\n                    \
    \                                \"vertical direction.\",\n                  \
    \                   \"examples\": [10],\n                                    \
    \ \"minimum\": 1,\n                                     \"title\": \"The RegionHeight\
    \ schema\",\n                                     \"type\": \"integer\"},\n  \
    \                  \"RegionWidth\": {\"$id\": \"#/properties/RegionWidth\",\n\
    \                                    \"default\": 1,\n                       \
    \             \"description\": \"The number of tiles \"\n                    \
    \                               \"per region in \"\n                         \
    \                          \"horizontal direction.\",\n                      \
    \              \"examples\": [10],\n                                    \"minimum\"\
    : 1,\n                                    \"title\": \"The RegionWidth schema\"\
    ,\n                                    \"type\": \"integer\"},\n             \
    \       \"ResolutionX\": {\"$id\": \"#/properties/ResolutionX\",\n           \
    \                         \"default\": 0.0,\n                                \
    \    \"description\": \"Physical size of a \"\n                              \
    \                     \"pixel.\",\n                                    \"examples\"\
    : [300.0],\n                                    \"minimum\": 0.0,\n          \
    \                          \"title\": \"The ResolutionX schema\",\n          \
    \                          \"type\": \"number\"},\n                    \"ResolutionXUnit\"\
    : {\"$id\": \"#/properties/ResolutionXUnit\",\n                              \
    \          \"default\": \"nm\",\n                                        \"description\"\
    : \"The units of the \"\n                                                    \
    \   \"physical size of a \"\n                                                \
    \       \"pixel.\",\n                                        \"enum\": [\"m\"\
    ,\n                                                 \"dm\",\n                \
    \                                 \"cm\",\n                                  \
    \               \"mm\",\n                                                 \"um\"\
    ,\n                                                 \"nm\",\n                \
    \                                 \"pm\",\n                                  \
    \               \"fm\"],\n                                        \"examples\"\
    : [\"nm\"],\n                                        \"title\": \"The ResolutionXUnit\
    \ \"\n                                                 \"schema\",\n         \
    \                               \"type\": \"string\"},\n                    \"\
    ResolutionY\": {\"$id\": \"#/properties/ResolutionY\",\n                     \
    \               \"default\": 0.0,\n                                    \"description\"\
    : \"Physical size of a \"\n                                                  \
    \ \"pixel.\",\n                                    \"examples\": [300.0],\n  \
    \                                  \"minimum\": 0.0,\n                       \
    \             \"title\": \"The ResolutionY schema\",\n                       \
    \             \"type\": \"number\"},\n                    \"ResolutionYUnit\"\
    : {\"$id\": \"#/properties/ResolutionYUnit\",\n                              \
    \          \"default\": \"nm\",\n                                        \"description\"\
    : \"The units of the \"\n                                                    \
    \   \"physical size of a \"\n                                                \
    \       \"pixel.\",\n                                        \"enum\": [\"m\"\
    ,\n                                                 \"dm\",\n                \
    \                                 \"cm\",\n                                  \
    \               \"mm\",\n                                                 \"um\"\
    ,\n                                                 \"nm\",\n                \
    \                                 \"pm\",\n                                  \
    \               \"fm\"],\n                                        \"examples\"\
    : [\"nm\"],\n                                        \"title\": \"The ResolutionYUnit\
    \ \"\n                                                 \"schema\",\n         \
    \                               \"type\": \"string\"},\n                    \"\
    ResolutionZ\": {\"$id\": \"#/properties/ResolutionZ\",\n                     \
    \               \"default\": 0.0,\n                                    \"description\"\
    : \"Physical size of a \"\n                                                  \
    \ \"pixel.\",\n                                    \"examples\": [100.0],\n  \
    \                                  \"minimum\": 0.0,\n                       \
    \             \"title\": \"The ResolutionZ schema\",\n                       \
    \             \"type\": \"number\"},\n                    \"ResolutionZUnit\"\
    : {\"$id\": \"#/properties/ResolutionZUnit\",\n                              \
    \          \"default\": \"nm\",\n                                        \"description\"\
    : \"The units of the \"\n                                                    \
    \   \"physical size of a \"\n                                                \
    \       \"pixel.\",\n                                        \"enum\": [\"m\"\
    ,\n                                                 \"dm\",\n                \
    \                                 \"cm\",\n                                  \
    \               \"mm\",\n                                                 \"um\"\
    ,\n                                                 \"nm\",\n                \
    \                                 \"pm\",\n                                  \
    \               \"fm\"],\n                                        \"examples\"\
    : [\"nm\"],\n                                        \"title\": \"The ResolutionZUnit\
    \ \"\n                                                 \"schema\",\n         \
    \                               \"type\": \"string\"},\n                    \"\
    TileHeight\": {\"$id\": \"#/properties/TileHeight\",\n                       \
    \            \"default\": 1,\n                                   \"description\"\
    : \"The size of a tile \"\n                                                  \"\
    vertical direction in \"\n                                                  \"\
    pixels.\",\n                                   \"examples\": [2048],\n       \
    \                            \"minimum\": 1,\n                               \
    \    \"title\": \"The TileHeight schema\",\n                                 \
    \  \"type\": \"integer\"},\n                    \"TileLayout\": {\"$id\": \"#/properties/TileLayout\"\
    ,\n                                   \"default\": \"Snake\",\n              \
    \                     \"description\": \"The way tiles are \"\n              \
    \                                    \"captured by the \"\n                  \
    \                                \"microscope.\",\n                          \
    \         \"enum\": [\"Snake\", \"Grid\"],\n                                 \
    \  \"examples\": [\"Snake\"],\n                                   \"title\": \"\
    The TileLayout schema\",\n                                   \"type\": \"string\"\
    },\n                    \"TileOverlapX\": {\"$id\": \"#/properties/TileOverlapX\"\
    ,\n                                     \"default\": 0.0,\n                  \
    \                   \"description\": \"The horizontal \"\n                   \
    \                                 \"overlap between \"\n                     \
    \                               \"neighbouring tiles in \"\n                 \
    \                                   \"fractions of one.\",\n                 \
    \                    \"examples\": [0.3],\n                                  \
    \   \"exclusiveMaximum\": 1.0,\n                                     \"minimum\"\
    : 0.0,\n                                     \"title\": \"The TileOverlapX schema\"\
    ,\n                                     \"type\": \"number\"},\n             \
    \       \"TileOverlapY\": {\"$id\": \"#/properties/TileOverlapY\",\n         \
    \                            \"default\": 0.0,\n                             \
    \        \"description\": \"The vertical overlap \"\n                        \
    \                            \"between neighbouring \"\n                     \
    \                               \"tiles in fractions of \"\n                 \
    \                                   \"one.\",\n                              \
    \       \"examples\": [0.3],\n                                     \"exclusiveMaximum\"\
    : 1.0,\n                                     \"minimum\": 0.0,\n             \
    \                        \"title\": \"The TileOverlapY schema\",\n           \
    \                          \"type\": \"number\"},\n                    \"TileWidth\"\
    : {\"$id\": \"#/properties/TileWidth\",\n                                  \"\
    default\": 1,\n                                  \"description\": \"The size of\
    \ a tile \"\n                                                 \"horizontal direction\
    \ in \"\n                                                 \"pixels.\",\n     \
    \                             \"examples\": [2048],\n                        \
    \          \"minimum\": 1,\n                                  \"title\": \"The\
    \ TileWidth schema\",\n                                  \"type\": \"integer\"\
    },\n                    \"Version\": {\"$id\": \"#/properties/Version\",\n   \
    \                             \"default\": \"1.0\",\n                        \
    \        \"description\": \"The version of CODEX \"\n                        \
    \                       \"metadata.\",\n                                \"examples\"\
    : [\"1.0\"],\n                                \"title\": \"The Version schema\"\
    ,\n                                \"type\": \"string\"}},\n     \"required\"\
    : [\"Version\",\n                  \"DatasetName\",\n                  \"ImmersionMedium\"\
    ,\n                  \"NominalMagnification\",\n                  \"NumericalAperture\"\
    ,\n                  \"ResolutionX\",\n                  \"ResolutionXUnit\",\n\
    \                  \"ResolutionY\",\n                  \"ResolutionYUnit\",\n\
    \                  \"ResolutionZ\",\n                  \"ResolutionZUnit\",\n\
    \                  \"BitDepth\",\n                  \"NumRegions\",\n        \
    \          \"NumCycles\",\n                  \"NumZPlanes\",\n               \
    \   \"NumChannels\",\n                  \"RegionWidth\",\n                  \"\
    RegionHeight\",\n                  \"TileWidth\",\n                  \"TileHeight\"\
    ,\n                  \"TileOverlapX\",\n                  \"TileOverlapY\",\n\
    \                  \"TileLayout\",\n                  \"NuclearStainForSegmentation\"\
    ,\n                  \"MembraneStainForSegmentation\",\n                  \"ChannelDetails\"\
    ],\n     \"title\": \"The root schema\",\n     \"type\": \"object\"}\n\nOn instance:\n\
    \    {}."
  Recursively test all tiff files that are not ome.tiffs for validity:
  - '/home/gesina/code/ingest-validation-tools/examples/plugin-tests/prev-gen-codex-expected-failure/upload/dataset-1/src_something/cycX_regX_X/X_X_ZX_CHX.tif
    is not a valid TIFF file: not a TIFF file.'
Hint: 'If validation fails because of extra whitespace in the TSV, try:

  src/cleanup_whitespace.py --tsv_in original.tsv --tsv_out clean.tsv.'
```
