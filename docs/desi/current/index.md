---
title: DESI
schema_name: desi
category: Imaging Mass Spectrometry (IMS)
all_versions_deprecated: False
exclude_from_index: False
layout: default

---
Prepare your metadata based on the latest metadata schema using one of the template files below. See the instructions in the [Metadata Validation Workflow](https://docs.google.com/document/d/1lfgiDGbyO4K4Hz1FMsJjmJd9RdwjShtJqFYNwKpbcZY) document for more information on preparing and validating your metadata.tsv file prior to submission.
This is the most recent metadata specification that needs to be followed for the submission of new data. See the [harmonized specification](https://docs.hubmapconsortium.org/assays/metadata/desi.html) for a view of the metadata across this and any previous versions.

Related files:


- [📝 Excel template](https://raw.githubusercontent.com/hubmapconsortium/dataset-metadata-spreadsheet/main/desi/latest/desi.xlsx): For metadata entry.
- [📝 TSV template](https://raw.githubusercontent.com/hubmapconsortium/dataset-metadata-spreadsheet/main/desi/latest/desi.tsv): Alternative for metadata entry.


[This link](https://docs.google.com/spreadsheets/d/1YnmdTAA0Z9MKN3OjR3Sca8pz-LNQll91wdQoRPSP6Q4/edit#gid=0) lists the set of fields that are required in the OME TIFF file XML header.

<a name="metadata-schema"></a>
## [Metadata schema](#metadata-schema)


<summary><a href="https://openview.metadatacenter.org/templates/https:%2F%2Frepo.metadatacenter.org%2Ftemplates%2F01d909d8-84a8-4362-9e42-782bc4da0eec"><b>Version 2 (use this one)</b></a></summary>



<br>

<a name="directory-schemas"></a>
## [Directory schemas](#directory-schemas)
<summary><b>Version 2.3 (use this one)</b></summary>

| pattern | required? | description |
| --- | --- | --- |
| <code>extras\/.*</code> | ✓ | Folder for general lab-specific files related to the dataset. |
| <code>extras\/mass-spec_environment\.(?:json&#124;tsv)$</code> |  | JSON or TSV file containing the machine parameters/settings. This is akin to the microscope_environment.json file that's used to describe the imaging equipment. |
| <code>raw\/.*</code> | ✓ | Raw data files for the experiment. |
| <code>raw\/imzML\/.*</code> | ✓ | Raw mass spec data. |
| <code>raw\/imzML\/[^\/]+\.ibd$</code> | ✓ | Mass spec data saved in a binary format. |
| <code>raw\/imzML\/[^\/]+\.imzML$</code> | ✓ | Mass spec metadata saved in XML format. Index to .ibd file. |
| <code>lab_processed\/.*</code> | ✓ | Experiment files that were processed by the lab generating the data. |
| <code>lab_processed\/images\/.*</code> | ✓ | Processed image files |
| <code>lab_processed\/images\/[^\/]+\.ome\.tiff$</code> | ✓ | OME-TIFF files (multichannel, multi-layered) produced by the microscopy experiment. If compressed, must use loss-less compression algorithm. See the following link for the set of fields that are required in the OME TIFF file XML header. <https://docs.google.com/spreadsheets/d/1YnmdTAA0Z9MKN3OjR3Sca8pz-LNQll91wdQoRPSP6Q4/edit#gid=0> |
| <code>lab_processed\/images\/[^\/]*ome-tiff\.channels\.csv$</code> | ✓ | This file provides essential documentation pertaining to each channel of the accommpanying OME TIFF. The file should contain one row per OME TIFF channel. The required fields are detailed <https://docs.google.com/spreadsheets/d/1xEJSb0xn5C5fB3k62pj1CyHNybpt4-YtvUs5SUMS44o/edit#gid=0> |
| <code>lab_processed\/transformations\/.*</code> |  | Directory containing image transformations. |
| <code>lab_processed\/transformations\/[^\/]+\.txt$</code> |  | Transformations/map back to autofluorescence microscopy (related) data |
| <code>lab_processed\/annotations\/.*</code> | ✓ | Directory containing annotations |
| <code>lab_processed\/annotations\/[^\/]+_MolecularAssignments\.tsv$</code> | ✓ | TSV file containing the m/z, molecular assignment, etc. |

<summary><b>Version 2.2</b></summary>

| pattern | required? | description |
| --- | --- | --- |
| <code>extras\/.*</code> | ✓ | Folder for general lab-specific files related to the dataset. |
| <code>extras\/mass-spec_environment\.(?:json&#124;tsv)$</code> |  | JSON or TSV file containing the machine parameters/settings. This is akin to the microscope_environment.json file that's used to describe the imaging equipment. |
| <code>raw\/.*</code> | ✓ | Raw data files for the experiment. |
| <code>raw\/imzML\/.*</code> | ✓ | Raw mass spec data. |
| <code>raw\/imzML\/[^\/]+\.ibd$</code> | ✓ | Mass spec data saved in a binary format. |
| <code>raw\/imzML\/[^\/]+\.imzML$</code> | ✓ | Mass spec metadata saved in XML format. Index to .ibd file. |
| <code>lab_processed\/.*</code> | ✓ | Experiment files that were processed by the lab generating the data. |
| <code>lab_processed\/images\/.*</code> | ✓ | Processed image files |
| <code>lab_processed\/images\/[^\/]+\.ome\.(?:tif&#124;tiff)$</code> | ✓ | OME-TIFF files (multichannel, multi-layered) produced by the microscopy experiment. If compressed, must use loss-less compression algorithm. See the following link for the set of fields that are required in the OME TIFF file XML header. <https://docs.google.com/spreadsheets/d/1YnmdTAA0Z9MKN3OjR3Sca8pz-LNQll91wdQoRPSP6Q4/edit#gid=0> |
| <code>lab_processed\/images\/[^\/]*ome-(?:tif&#124;tiff)\.channels\.csv$</code> | ✓ | This file provides essential documentation pertaining to each channel of the accommpanying OME TIFF. The file should contain one row per OME TIFF channel. The required fields are detailed <https://docs.google.com/spreadsheets/d/1xEJSb0xn5C5fB3k62pj1CyHNybpt4-YtvUs5SUMS44o/edit#gid=0> |
| <code>lab_processed\/transformations\/.*</code> |  | Directory containing image transformations. |
| <code>lab_processed\/transformations\/[^\/]+\.txt$</code> |  | Transformations/map back to autofluorescence microscopy (related) data |
| <code>lab_processed\/annotations\/.*</code> | ✓ | Directory containing annotations |
| <code>lab_processed\/annotations\/[^\/]+_MolecularAssignments\.tsv$</code> | ✓ | TSV file containing the m/z, molecular assignment, etc. |

<summary><b>Version 2.1</b></summary>

| pattern | required? | description |
| --- | --- | --- |
| <code>extras\/.*</code> | ✓ | Folder for general lab-specific files related to the dataset. |
| <code>extras\/mass-spec_environment\.(?:json&#124;tsv)$</code> |  | JSON or TSV file containing the machine parameters/settings. This is akin to the microscope_environment.json file that's used to describe the imaging equipment. |
| <code>raw\/.*</code> | ✓ | Raw data files for the experiment. |
| <code>raw\/imzML\/.*</code> | ✓ | Raw mass spec data. |
| <code>raw\/imzML\/[^\/]+\.ibd$</code> | ✓ | Mass spec data saved in a binary format. |
| <code>raw\/imzML\/[^\/]+\.imzML$</code> | ✓ | Mass spec metadata saved in XML format. Index to .ibd file. |
| <code>lab_processed\/.*</code> | ✓ | Experiment files that were processed by the lab generating the data. |
| <code>lab_processed\/images\/.*</code> | ✓ | Processed image files |
| <code>lab_processed\/images\/[^\/]+\.ome\.tiff$</code> | ✓ | OME-TIFF files (multichannel, multi-layered) produced by the microscopy experiment. If compressed, must use loss-less compression algorithm. See the following link for the set of fields that are required in the OME TIFF file XML header. <https://docs.google.com/spreadsheets/d/1YnmdTAA0Z9MKN3OjR3Sca8pz-LNQll91wdQoRPSP6Q4/edit#gid=0> |
| <code>lab_processed\/images\/[^\/]*ome-tiff\.channels\.csv$</code> | ✓ | This file provides essential documentation pertaining to each channel of the accommpanying OME TIFF. The file should contain one row per OME TIFF channel. The required fields are detailed <https://docs.google.com/spreadsheets/d/1xEJSb0xn5C5fB3k62pj1CyHNybpt4-YtvUs5SUMS44o/edit#gid=0> |
| <code>lab_processed\/transformations\/.*</code> |  | Directory containing image transformations. |
| <code>lab_processed\/transformations\/[^\/]+\.txt$</code> |  | Transformations/map back to autofluorescence microscopy (related) data |
| <code>lab_processed\/annotations\/.*</code> | ✓ | Directory containing annotations |
| <code>lab_processed\/annotations\/[^\/]+_MolecularAssignments\.tsv$</code> | ✓ | TSV file containing the m/z, molecular assignment, etc. |

<summary><b>Version 2.0</b></summary>

| pattern | required? | description |
| --- | --- | --- |
| <code>extras\/.*</code> | ✓ | Folder for general lab-specific files related to the dataset. |
| <code>extras\/mass-spec_environment\.(?:json&#124;tsv)</code> |  | JSON or TSV file containing the machine parameters/settings. This is akin to the microscope_environment.json file that's used to describe the imaging equipment. |
| <code>raw\/.*</code> | ✓ | Raw data files for the experiment. |
| <code>raw\/imzML\/.*</code> | ✓ | Raw mass spec data. |
| <code>raw\/imzML\/[^\/]+\.ibd</code> | ✓ | Mass spec data saved in a binary format. |
| <code>raw\/imzML\/[^\/]+\.imzML</code> | ✓ | Mass spec metadata saved in XML format. Index to .ibd file. |
| <code>lab_processed\/.*</code> | ✓ | Experiment files that were processed by the lab generating the data. |
| <code>lab_processed\/images\/.*</code> | ✓ | Processed image files |
| <code>lab_processed\/images\/[^\/]+\.ome\.tiff</code> | ✓ | OME-TIFF files (multichannel, multi-layered) produced by the microscopy experiment. If compressed, must use loss-less compression algorithm. See the following link for the set of fields that are required in the OME TIFF file XML header. <https://docs.google.com/spreadsheets/d/1YnmdTAA0Z9MKN3OjR3Sca8pz-LNQll91wdQoRPSP6Q4/edit#gid=0> |
| <code>lab_processed\/images\/[^\/]*ome-tiff\.channels\.csv</code> | ✓ | This file provides essential documentation pertaining to each channel of the accommpanying OME TIFF. The file should contain one row per OME TIFF channel. The required fields are detailed <https://docs.google.com/spreadsheets/d/1xEJSb0xn5C5fB3k62pj1CyHNybpt4-YtvUs5SUMS44o/edit#gid=0> |
| <code>lab_processed\/transformations\/.*</code> |  | Directory containing image transformations. |
| <code>lab_processed\/transformations\/[^\/]+\.txt</code> |  | Transformations/map back to autofluorescence microscopy (related) data |
| <code>lab_processed\/annotations\/.*</code> | ✓ | Directory containing annotations |
| <code>lab_processed\/annotations\/[^\/]+_MolecularAssignments\.tsv</code> | ✓ | TSV file containing the m/z, molecular assignment, etc. |

