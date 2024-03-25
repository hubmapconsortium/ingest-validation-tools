---
title: Multiplex Ion Beam Imaging
schema_name: mibi
category: Imaging Mass Spectrometry (IMS)
all_versions_deprecated: False
exclude_from_index: False
layout: default

---
Prepare your metadata based on the latest metadata schema using one of the template files below. See the instructions in the [Metadata Validation Workflow](https://docs.google.com/document/d/1lfgiDGbyO4K4Hz1FMsJjmJd9RdwjShtJqFYNwKpbcZY) document for more information on preparing and validating your metadata.tsv file prior to submission.

Related files:


- [📝 Excel template](https://raw.githubusercontent.com/hubmapconsortium/dataset-metadata-spreadsheet/main/mibi/latest/mibi.xlsx): For metadata entry.
- [📝 TSV template](https://raw.githubusercontent.com/hubmapconsortium/dataset-metadata-spreadsheet/main/mibi/latest/mibi.tsv): Alternative for metadata entry.


[This link](https://docs.google.com/spreadsheets/d/1YnmdTAA0Z9MKN3OjR3Sca8pz-LNQll91wdQoRPSP6Q4/edit#gid=0) lists the set of fields that are required in the OME TIFF file XML header.

## Metadata schema


<summary><a href="https://openview.metadatacenter.org/templates/https:%2F%2Frepo.metadatacenter.org%2Ftemplates%2F784cfaa7-4a73-4173-b639-b24e0ed76155"><b>Version 2 (use this one)</b></a></summary>



<br>

## Directory schemas
<summary><b>Version 2.0 (use this one)</b></summary>

| pattern | required? | description |
| --- | --- | --- |
| <code>extras\/.*</code> | ✓ | Folder for general lab-specific files related to the dataset. [Exists in all assays] |
| <code>extras\/hardware\.json</code> | ✓ | JSON file containing the machine parameters/settings. This is akin to the microscope_environment.json file that's used to describe the imaging equipment. |
| <code>raw\/.*</code> | ✓ | This is a directory containing raw data. |
| <code>raw\/images\/.*</code> | ✓ | Raw image files. Using this subdirectory allows for harmonization with other more complex assays, like Visium that includes both raw imaging and sequencing data. |
| <code>raw\/images\/[^\/]+\.ome\.tiff</code> | ✓ | Raw image file. |
| <code>raw\/images\/tiles\.csv</code> |  | This file contains the approximate coordinates for each of the tiled raw images. |
| <code>lab_processed\/.*</code> | ✓ | Experiment files that were processed by the lab generating the data. |
| <code>lab_processed\/images\/.*</code> | ✓ | This is a directory containing processed image files |
| <code>lab_processed\/images\/[^\/]+\.ome\.tiff</code> | ✓ | OME-TIFF file (multichannel, multi-layered) produced by the experiment. If compressed, must use loss-less compression algorithm. See the following link for the set of fields that are required in the OME TIFF file XML header. <https://docs.google.com/spreadsheets/d/1YnmdTAA0Z9MKN3OjR3Sca8pz-LNQll91wdQoRPSP6Q4/edit#gid=0> |
| <code>lab_processed\/images\/[^\/]*ome-tiff\.channels\.csv</code> | ✓ | This file provides essential documentation pertaining to each channel of the accommpanying OME TIFF. The file should contain one row per OME TIFF channel. The required fields are detailed <https://docs.google.com/spreadsheets/d/1xEJSb0xn5C5fB3k62pj1CyHNybpt4-YtvUs5SUMS44o/edit#gid=0> |

