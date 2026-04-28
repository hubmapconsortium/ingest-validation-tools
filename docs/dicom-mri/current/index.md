---
title: DICOM-MRI
schema_name: dicom-mri
category: Clinical Imaging Modalities
all_versions_deprecated: False
exclude_from_index: False
layout: default

---
Related files:

- [📝 Excel template](https://raw.githubusercontent.com/hubmapconsortium/dataset-metadata-spreadsheet/main/dicom-mri/latest/dicom-mri.xlsx): For metadata entry.
- [📝 TSV template](https://raw.githubusercontent.com/hubmapconsortium/dataset-metadata-spreadsheet/main/dicom-mri/latest/dicom-mri.tsv): Alternative for metadata entry.


The process for uploading clinical imaging data is different than that for experimental assay data. 

All clinical imaging data must be uploaded in DICOM format. 

Given the potential inclusion of personally identifiable information (PII) in clinical imaging, the imaging files must be uploaded directly to a dedicated directory in a secure Globus endpoint. Sites with clinical imaging data should begin by emailing the Help Desk to have a directory created. Please include the Globus Identity and Globus ID of the individual who will be performing the upload in your email. 

Once the upload of the clinical imaging data in the structure described below is complete, the Help Desk should again be notified. Following notification: 
- metadata will be extracted from the headers of the DICOM files
- an XLSX file containing the extracted metadata will be emailed to the uploader
- the uploader will complete the required fields, validate the file and upload it to the Globus directory previously created for the DICOM files 

The DICOM files will then be de-identified to HIPAA safe harbor standards by the HIVE/CODCC for publication.

## Metadata schema


<summary><a href="https://openview.metadatacenter.org/templates/https:%2F%2Frepo.metadatacenter.org%2Ftemplates%2Ff8c76a33-6262-4733-8f00-23175af7fd73"><b>Version 2 (use this one)</b></a></summary>



<br>

## Directory schemas
<summary><b>Version 2.0 (use this one)</b></summary>

| pattern | required? | description |
| --- | --- | --- |
| <code>extras\/.*</code> | ✓ | Folder for general lab-specific files related to the dataset. |
| <code>raw\/.*</code> | ✓ | This is a directory containing raw data. |
| <code>raw\/images\/.*</code> | ✓ | This is a directory containing raw MRI DICOM files. |
| <code>raw\/images\/[^\/]+\.dcm$</code> | ✓ | All relevant MRI DICOM files. |

