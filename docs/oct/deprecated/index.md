---
title: OCT
schema_name: oct
category: Clinical Imaging Modalities
all_versions_deprecated: False
exclude_from_index: False
layout: default
permalink: /oct/
---

Related files:


- [📝 Excel template](https://raw.githubusercontent.com/hubmapconsortium/ingest-validation-tools/main/docs/oct/oct-metadata.xlsx): For metadata entry.
- [📝 TSV template](https://raw.githubusercontent.com/hubmapconsortium/ingest-validation-tools/main/docs/oct/oct-metadata.tsv): Alternative for metadata entry.


This schema is for clinical imaging using optical coherence tomography (OCT).

## Metadata schema


<details markdown="1" open="true"><summary><b>Version 1 (use this one)</b></summary>

<blockquote markdown="1">

<details markdown="1"><summary>Shared by all types</summary>

[`version`](#version)<br>
[`description`](#description)<br>
[`donor_id`](#donor_id)<br>
[`tissue_id`](#tissue_id)<br>
[`execution_datetime`](#execution_datetime)<br>
[`protocols_io_doi`](#protocols_io_doi)<br>
[`operator`](#operator)<br>
[`operator_email`](#operator_email)<br>
[`pi`](#pi)<br>
[`pi_email`](#pi_email)<br>
[`assay_category`](#assay_category)<br>
[`assay_type`](#assay_type)<br>
[`acquisition_instrument_vendor`](#acquisition_instrument_vendor)<br>
[`acquisition_instrument_model`](#acquisition_instrument_model)<br>

</details>
<details markdown="1"><summary>Shared by all clinical imaging assays</summary>

[`single_file_export_format`](#single_file_export_format)<br>
[`max_x_width_value`](#max_x_width_value)<br>
[`max_x_width_unit`](#max_x_width_unit)<br>
[`max_y_height_value`](#max_y_height_value)<br>
[`max_y_height_unit`](#max_y_height_unit)<br>
[`roi_description`](#roi_description)<br>
[`roi_id`](#roi_id)<br>
[`resolution_x_value`](#resolution_x_value)<br>
[`resolution_x_unit`](#resolution_x_unit)<br>
[`resolution_y_value`](#resolution_y_value)<br>
[`resolution_y_unit`](#resolution_y_unit)<br>
[`resolution_z_value`](#resolution_z_value)<br>
[`resolution_z_unit`](#resolution_z_unit)<br>
[`pixel_size_z_value`](#pixel_size_z_value)<br>
[`pixel_size_z_unit`](#pixel_size_z_unit)<br>
[`number_of_images`](#number_of_images)<br>

</details>
<details markdown="1"><summary>Unique to this type</summary>

[`total_sections_analyzed`](#total_sections_analyzed)<br>
[`wavelength_value`](#wavelength_value)<br>
[`wavelength_unit`](#wavelength_unit)<br>
[`volume_export_format`](#volume_export_format)<br>
[`sn_quality`](#sn_quality)<br>
[`sn_quality_unit`](#sn_quality_unit)<br>
[`contributors_path`](#contributors_path)<br>
[`data_path`](#data_path)<br>
</details>

</blockquote>

### Shared by all types

<a name="version"></a>
##### [`version`](#version)
Version of the schema to use when validating this metadata.

| constraint | value |
| --- | --- |
| enum | `1` |
| required | `True` |

<a name="description"></a>
##### [`description`](#description)
Free-text description of this assay.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="donor_id"></a>
##### [`donor_id`](#donor_id)
HuBMAP Display ID of the donor of the assayed tissue. Example: `ABC123`.

| constraint | value |
| --- | --- |
| pattern (regular expression) | <code>[A-Z]+[0-9]+</code> |
| required | `True` |

<a name="tissue_id"></a>
##### [`tissue_id`](#tissue_id)
HuBMAP Display ID of the assayed tissue. Example: `ABC123-BL-1-2-3_456`.

| constraint | value |
| --- | --- |
| pattern (regular expression) | <code>(([A-Z]+[0-9]+)-[A-Z]{2}\d*(-\d+)+(_\d+)?)(,([A-Z]+[0-9]+)-[A-Z]{2}\d*(-\d+)+(_\d+)?)*</code> |
| required | `True` |

<a name="execution_datetime"></a>
##### [`execution_datetime`](#execution_datetime)
Start date and time of assay, typically a date-time stamped folder generated by the acquisition instrument. YYYY-MM-DD hh:mm, where YYYY is the year, MM is the month with leading 0s, and DD is the day with leading 0s, hh is the hour with leading zeros, mm are the minutes with leading zeros.

| constraint | value |
| --- | --- |
| type | `datetime` |
| format | `%Y-%m-%d %H:%M` |
| required | `True` |

<a name="protocols_io_doi"></a>
##### [`protocols_io_doi`](#protocols_io_doi)
DOI for protocols.io referring to the protocol for this assay.

| constraint | value |
| --- | --- |
| required | `True` |
| pattern (regular expression) | <code>10\.17504/.*</code> |
| url | prefix: <code>https://dx.doi.org/</code> |

<a name="operator"></a>
##### [`operator`](#operator)
Name of the person responsible for executing the assay.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="operator_email"></a>
##### [`operator_email`](#operator_email)
Email address for the operator.

| constraint | value |
| --- | --- |
| format | `email` |
| required | `True` |

<a name="pi"></a>
##### [`pi`](#pi)
Name of the principal investigator responsible for the data.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="pi_email"></a>
##### [`pi_email`](#pi_email)
Email address for the principal investigator.

| constraint | value |
| --- | --- |
| format | `email` |
| required | `True` |

<a name="assay_category"></a>
##### [`assay_category`](#assay_category)
Each assay is placed into one of the following 4 general categories: generation of images of microscopic entities, identification & quantitation of molecules by mass spectrometry, imaging mass spectrometry, and determination of nucleotide sequence.

| constraint | value |
| --- | --- |
| enum | `clinical_imaging` |
| required | `True` |

<a name="assay_type"></a>
##### [`assay_type`](#assay_type)
The specific type of assay being executed.

| constraint | value |
| --- | --- |
| enum | `OCT` |
| required | `True` |

<a name="acquisition_instrument_vendor"></a>
##### [`acquisition_instrument_vendor`](#acquisition_instrument_vendor)
An acquisition instrument is the device that contains the signal detection hardware and signal processing software. Assays generate signals such as light of various intensities or color or signals representing the molecular mass.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="acquisition_instrument_model"></a>
##### [`acquisition_instrument_model`](#acquisition_instrument_model)
Manufacturers of an acquisition instrument may offer various versions (models) of that instrument with different features or sensitivities. Differences in features or sensitivities may be relevant to processing or interpretation of the data.

| constraint | value |
| --- | --- |
| required | `True` |

### Shared by all clinical imaging assays

<a name="single_file_export_format"></a>
##### [`single_file_export_format`](#single_file_export_format)
The format in which each single imaging file will be exported. (Example: DICOM, tiff, avi, etc.)

| constraint | value |
| --- | --- |
| required | `True` |

<a name="max_x_width_value"></a>
##### [`max_x_width_value`](#max_x_width_value)
Image width value of the ROI acquisition.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

<a name="max_x_width_unit"></a>
##### [`max_x_width_unit`](#max_x_width_unit)
Units of image width of the ROI acquisition. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| enum | `um` or `mm` |
| required | `False` |
| required if | `max_x_width_value` present |

<a name="max_y_height_value"></a>
##### [`max_y_height_value`](#max_y_height_value)
Image height value of the ROI acquisition.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

<a name="max_y_height_unit"></a>
##### [`max_y_height_unit`](#max_y_height_unit)
Units of image height of the ROI acquisition. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| enum | `um` or `mm` |
| required | `False` |
| required if | `max_y_height_value` present |

<a name="roi_description"></a>
##### [`roi_description`](#roi_description)
A description of the region of interest (ROI) captured in the image.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="roi_id"></a>
##### [`roi_id`](#roi_id)
Multiple images (1-n) are acquired from regions of interest (ROI1, ROI2, ROI3, etc) on a slide. The roi_id is a number from 1-n representing the ROI captured on a slide. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| type | `integer` |
| required | `False` |
| minimum | `1` |

<a name="resolution_x_value"></a>
##### [`resolution_x_value`](#resolution_x_value)
The width of a pixel.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

<a name="resolution_x_unit"></a>
##### [`resolution_x_unit`](#resolution_x_unit)
The unit of measurement of the width of a pixel. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| enum | `nm`, `um`, or `mm` |
| required | `False` |
| required if | `resolution_x_value` present |

<a name="resolution_y_value"></a>
##### [`resolution_y_value`](#resolution_y_value)
The height of a pixel.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

<a name="resolution_y_unit"></a>
##### [`resolution_y_unit`](#resolution_y_unit)
The unit of measurement of the height of a pixel. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| enum | `nm`, `um`, or `mm` |
| required | `False` |
| required if | `resolution_y_value` present |

<a name="resolution_z_value"></a>
##### [`resolution_z_value`](#resolution_z_value)
Optional if assay does not have multiple z-levels. Note that this is resolution within a given sample: z-pitch (resolution_z_value) is the increment distance between image slices, ie. the microscope stage is moved up or down in increments to capture images of several focal planes. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `False` |

<a name="resolution_z_unit"></a>
##### [`resolution_z_unit`](#resolution_z_unit)
The unit of incremental distance between image slices.(um) Leave blank if not applicable.

| constraint | value |
| --- | --- |
| enum | `nm`, `um`, or `mm` |
| required | `False` |
| required if | `resolution_z_value` present |

<a name="pixel_size_z_value"></a>
##### [`pixel_size_z_value`](#pixel_size_z_value)
Depth value of the pixel or voxel measurement (distinct from the image resolution_z_value). Leave blank if not applicable.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `False` |

<a name="pixel_size_z_unit"></a>
##### [`pixel_size_z_unit`](#pixel_size_z_unit)
Depth unit of the pixel or voxel measurement. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| enum | `nm`, `um`, or `mm` |
| required | `False` |
| required if | `pixel_size_z_value` present |

<a name="number_of_images"></a>
##### [`number_of_images`](#number_of_images)
The total number of images in the dataset.

| constraint | value |
| --- | --- |
| type | `integer` |
| required | `True` |

### Unique to this type

<a name="total_sections_analyzed"></a>
##### [`total_sections_analyzed`](#total_sections_analyzed)
The number of sections used for analyzing microCT or OCT images. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| type | `integer` |
| required | `False` |

<a name="wavelength_value"></a>
##### [`wavelength_value`](#wavelength_value)
The value of the wavelength used to acquire OCT images (Example: 787) Leave blank if not applicable.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `False` |

<a name="wavelength_unit"></a>
##### [`wavelength_unit`](#wavelength_unit)
The unit of the wavelength value used to acquire OCT images (nm) Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |
| enum | `nm` |
| required if | `wavelength_value` present |

<a name="volume_export_format"></a>
##### [`volume_export_format`](#volume_export_format)
The format of the volume export of OCT images (Example: tiff) Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |
| enum | `tiff` or `avi` |

<a name="sn_quality"></a>
##### [`sn_quality`](#sn_quality)
An integer describing the signal to noise quality of an OCT image (Example: 30) Leave blank if not applicable.

| constraint | value |
| --- | --- |
| type | `integer` |
| required | `False` |

<a name="sn_quality_unit"></a>
##### [`sn_quality_unit`](#sn_quality_unit)
The unit of the integer describing the signal to noise quality of an OCT image (Example: dB) Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |
| enum | `dB` |
| required if | `sn_quality` present |

<a name="contributors_path"></a>
##### [`contributors_path`](#contributors_path)
Relative path to file with ORCID IDs for contributors for this dataset.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="data_path"></a>
##### [`data_path`](#data_path)
Relative path to file or directory with instrument data. Downstream processing will depend on filename extension conventions.

| constraint | value |
| --- | --- |
| required | `True` |

</details>



<br>
