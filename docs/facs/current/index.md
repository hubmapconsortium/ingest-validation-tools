---
title: FACS
schema_name: facs
category: Flow Cytometry
all_versions_deprecated: False
exclude_from_index: False
layout: default

---
Prepare your metadata based on the latest metadata schema using one of the template files below. See the instructions in the [Metadata Validation Workflow](https://docs.google.com/document/d/1lfgiDGbyO4K4Hz1FMsJjmJd9RdwjShtJqFYNwKpbcZY) document for more information on preparing and validating your metadata.tsv file prior to submission.

This is the most recent metadata specification that needs to be followed for the submission of new data. See the [harmonized specification](https://docs.hubmapconsortium.org/assays/metadata/facs.html) for a view of the metadata across this and any previous versions.

Related files:


- [📝 Excel template](https://raw.githubusercontent.com/hubmapconsortium/dataset-metadata-spreadsheet/main/facs/latest/facs.xlsx): For metadata entry.
- [📝 TSV template](https://raw.githubusercontent.com/hubmapconsortium/dataset-metadata-spreadsheet/main/facs/latest/facs.tsv): Alternative for metadata entry.




<a name="metadata-schema"></a>
## [Metadata schema](#metadata-schema)


<summary><a href="https://openview.metadatacenter.org/templates/https:%2F%2Frepo.metadatacenter.org%2Ftemplates%2Fdf335a89-b470-4c2c-a4c9-e8db7f166d59"><b>Version 2 (use this one)</b></a></summary>



<br>

<a name="directory-schemas"></a>
## [Directory schemas](#directory-schemas)
<summary><b>Version 2.0 (use this one)</b></summary>

| pattern | required? | description |
| --- | --- | --- |
| <code>extras\/.*</code> | ✓ | Folder for general lab-specific files related to the dataset. |
| <code>extras\/facs_hardware\.pdf$</code> | ✓ | File containing information about the configuration of the instrument, including:number of lasers, power, and wavelength of each; number of filters (if present) and band pass; number of detectors/PMTs. |
| <code>extras\/facs_hardware\.xlsx$</code> |  | File containing information about the configuration of the instrument, including:number of lasers, power, and wavelength of each; number of filters (if present) and band pass; number of detectors/PMTs. |
| <code>raw\/.*</code> | ✓ | This is a directory containing raw data. |
| <code>raw\/[^\/]+\.fcs$</code> |  | Contains the raw data from a mass cytometry experiment in a matrix where each row represents a single cell and each column represents a different metal-labeled antibody channel, with the values in each cell signifying the ion count detected for that specific metal on that cell, allowing for the analysis of multiple cell surface markers on individual cells. |
| <code>raw\/[^\/]+\.pdf$</code> |  | instrument QC and calibration file |
| <code>raw\/[^\/]+\.expt$</code> |  | Contains FACS experiment information (e.g., experiment template, sample names, metadata, etc) |
| <code>raw\/[^\/]+\.ust$</code> |  | Contains FACS instrument information (e.g., laser power, detector voltages, flow rates, thresholds) |
| <code>raw\/[^\/]+\.wtml$</code> |  | Contains FACS worksheets used using data acquisition/analysis |
| <code>raw\/[^\/]+\_bead_compensate\.wsp$</code> |  | FlowJo workspace file created by running specific compensation beads through the flow cytometer, which is then applied to your main experiment data to correct for fluorescence spillover. |
| <code>raw\/[^\/]+\.csv$</code> |  | Single file containing FACS vexperiment information from the instrument. |
| <code>lab_processed\/.*</code> | ✓ | Experiment files that were processed by the lab generating the data. |
| <code>lab_processed\/[^\/]+\.wsp$</code> | ✓ | **[QA/QC]** FlowJo workspace file corrected for flourescence spillover via application of the compensation WSP file described above. |

