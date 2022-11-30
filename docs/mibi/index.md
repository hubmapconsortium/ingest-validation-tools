---
title: Multiplex Ion Beam Imaging
schema_name: mibi
category: Imaging mass spectrometry
all_versions_deprecated: False
exclude_from_index: False
layout: default
---

Related files:

- [📝 Excel template](https://raw.githubusercontent.com/hubmapconsortium/ingest-validation-tools/main/docs/mibi/mibi-metadata.xlsx): For metadata entry.
- [📝 TSV template](https://raw.githubusercontent.com/hubmapconsortium/ingest-validation-tools/main/docs/mibi/mibi-metadata.tsv): Alternative for metadata entry.

This schema is for Multiplex Ion Beam Imaging (MIBI). For MIBI, the channel_id (in the Antibodies TSV) is the name of the metal tag on the corresponding antibody.  The other fields function the same way for all assays using antibodies.  For more information, see the [Antibodies TSV documentation](../antibodies).


## Directory schemas
### v0

| pattern | required? | description |
| --- | --- | --- |
| <code>mcd/[^/]+_HuBMAP_[^/]+_slide[^/]+\.zip</code> |  | Zipped CSV containing labels for sections as well as whether or not they were included in the 3D model. |
| <code>mcd/section_report\.csv</code> |  | Contains tissue id, acquisition id, 3D image ordering, MCD image ordering, and boolean if used for 3D model. |
| <code>mcd/channelnames_report\.csv</code> | ✓ | Contains antibodies names used and whether they were detected sufficiently or not. |
| <code>3D_image_stack\.ome\.tiff</code> | ✓ | OME.tiff file comprising all slices and channels. |
| <code>SingleCellData/cells\.csv</code> | ✓ | Contains one csv file per tissue with marker intensities (untransformed, range normalized to 99th percentile), phenograph cluster label and cell type label per single cell. |
| <code>SingleCellData/cellsinfo\.txt</code> |  | Text file containing formatting information about cellsorgan.csv. |
| <code>Mapping/cluster_labels_image\.tif</code> | ✓ | Cell image labeled by cell type. |
| <code>processed/umap_phenograph\.pdf</code> |  | tSNE phenograph. File is optional. |
| <code>processed/CellTypeComposition_perTissue\.pdf</code> |  | Cell type composition bar graph per tissue. File is optional. |
| <code>processed/Densityplots_perMarker\.pdf</code> |  | **[QA/QC]** Density plots of marker intensity, separated by marker. File is optional. |
| <code>processed/celltypes\.pdf</code> |  | Heatmap of marker expression per cluster, annotated by assigned cell type. File is optional. |
| <code>extras/.*</code> |  | Free-form descriptive information supplied by the TMC |



In the portal: Multiplex Ion Beam Imaging not in Portal

## Metadata schema

### Field types
- *Boolean* fields can be given as `TRUE`/`FALSE`, `True`/`False`, `true`/`false`, or `1`/`0`.  


<details markdown="1" open="true"><summary><b>Version 1 (current)</b></summary>

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
[`analyte_class`](#analyte_class)<br>
[`is_targeted`](#is_targeted)<br>
[`acquisition_instrument_vendor`](#acquisition_instrument_vendor)<br>
[`acquisition_instrument_model`](#acquisition_instrument_model)<br>

</details>
<details markdown="1"><summary>Unique to this type</summary>

[`number_of_antibodies`](#number_of_antibodies)<br>
[`number_of_channels`](#number_of_channels)<br>
[`resolution_x_value`](#resolution_x_value)<br>
[`resolution_x_unit`](#resolution_x_unit)<br>
[`resolution_y_value`](#resolution_y_value)<br>
[`resolution_y_unit`](#resolution_y_unit)<br>
[`max_x_width_value`](#max_x_width_value)<br>
[`max_x_width_unit`](#max_x_width_unit)<br>
[`max_y_height_value`](#max_y_height_value)<br>
[`max_y_height_unit`](#max_y_height_unit)<br>
[`roi_description`](#roi_description)<br>
[`roi_id`](#roi_id)<br>
[`acquisition_id`](#acquisition_id)<br>
[`area_normalized_ion_dose_unit`](#area_normalized_ion_dose_unit)<br>
[`area_normalized_ion_dose_value`](#area_normalized_ion_dose_value)<br>
[`data_precision_bytes`](#data_precision_bytes)<br>
[`dual_count_start`](#dual_count_start)<br>
[`end_datetime`](#end_datetime)<br>
[`pixel_dwell_time_value`](#pixel_dwell_time_value)<br>
[`pixel_dwell_time_unit`](#pixel_dwell_time_unit)<br>
[`pixel_size_x_value`](#pixel_size_x_value)<br>
[`pixel_size_x_unit`](#pixel_size_x_unit)<br>
[`pixel_size_y_value`](#pixel_size_y_value)<br>
[`pixel_size_y_unit`](#pixel_size_y_unit)<br>
[`preparation_instrument_vendor`](#preparation_instrument_vendor)<br>
[`preparation_instrument_model`](#preparation_instrument_model)<br>
[`primary_ion`](#primary_ion)<br>
[`primary_ion_current_value`](#primary_ion_current_value)<br>
[`primary_ion_current_unit`](#primary_ion_current_unit)<br>
[`reagent_prep_protocols_io_doi`](#reagent_prep_protocols_io_doi)<br>
[`section_prep_protocols_io_doi`](#section_prep_protocols_io_doi)<br>
[`segment_data_format`](#segment_data_format)<br>
[`signal_type`](#signal_type)<br>
[`start_datetime`](#start_datetime)<br>
[`antibodies_path`](#antibodies_path)<br>
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
| enum | `mass_spectrometry_imaging` |
| required | `True` |

<a name="assay_type"></a>
##### [`assay_type`](#assay_type)
The specific type of assay being executed.

| constraint | value |
| --- | --- |
| enum | `Multiplex Ion Beam Imaging` |
| required | `True` |

<a name="analyte_class"></a>
##### [`analyte_class`](#analyte_class)
Analytes are the target molecules being measured with the assay.

| constraint | value |
| --- | --- |
| enum | `protein` |
| required | `True` |

<a name="is_targeted"></a>
##### [`is_targeted`](#is_targeted)
Specifies whether or not a specific molecule(s) is/are targeted for detection/measurement by the assay.

| constraint | value |
| --- | --- |
| type | `boolean` |
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

### Unique to this type

<a name="number_of_antibodies"></a>
##### [`number_of_antibodies`](#number_of_antibodies)
Number of antibodies.

| constraint | value |
| --- | --- |
| type | `integer` |
| required | `True` |

<a name="number_of_channels"></a>
##### [`number_of_channels`](#number_of_channels)
Number of fluorescent channels imaged during each cycle.

| constraint | value |
| --- | --- |
| type | `integer` |
| required | `True` |

<a name="resolution_x_value"></a>
##### [`resolution_x_value`](#resolution_x_value)
The width of a pixel. (Akoya pixel is 377nm square)

| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

<a name="resolution_x_unit"></a>
##### [`resolution_x_unit`](#resolution_x_unit)
The unit of measurement of width of a pixel.(nm) Leave blank if not applicable.

| constraint | value |
| --- | --- |
| enum | `mm`, `um`, or `nm` |
| required | `False` |
| required if | `resolution_x_value` present |

<a name="resolution_y_value"></a>
##### [`resolution_y_value`](#resolution_y_value)
The height of a pixel. (Akoya pixel is 377nm square)

| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

<a name="resolution_y_unit"></a>
##### [`resolution_y_unit`](#resolution_y_unit)
The unit of measurement of height of a pixel. (nm) Leave blank if not applicable.

| constraint | value |
| --- | --- |
| enum | `mm`, `um`, or `nm` |
| required | `False` |
| required if | `resolution_y_value` present |

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
| enum | `um` |
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
| enum | `um` |
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
Multiple images (1-n) are acquired from regions of interest (ROI1, ROI2, ROI3, etc) on a slide. The roi_id is a number from 1-n representing the ROI captured on a slide.

| constraint | value |
| --- | --- |
| type | `integer` |
| required | `True` |

<a name="acquisition_id"></a>
##### [`acquisition_id`](#acquisition_id)
The acquisition_id refers to the directory containing the ROI images for a slide. Together, the acquisition_id and the roi_id indicate the slide-ROI represented in the image.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="area_normalized_ion_dose_unit"></a>
##### [`area_normalized_ion_dose_unit`](#area_normalized_ion_dose_unit)
Area normalized ion dose unit. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| enum | `nA*hr/mm2` |
| required | `False` |
| required if | `area_normalized_ion_dose_value` present |

<a name="area_normalized_ion_dose_value"></a>
##### [`area_normalized_ion_dose_value`](#area_normalized_ion_dose_value)
Number of primary ions delivered to the sample per unit area.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

<a name="data_precision_bytes"></a>
##### [`data_precision_bytes`](#data_precision_bytes)
Numerical data precision in bytes.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

<a name="dual_count_start"></a>
##### [`dual_count_start`](#dual_count_start)
Threshold for dual counting.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

<a name="end_datetime"></a>
##### [`end_datetime`](#end_datetime)
Time stamp indicating end of ablation for ROI.

| constraint | value |
| --- | --- |
| type | `datetime` |
| format | `%Y-%m-%d %H:%M` |
| required | `True` |

<a name="pixel_dwell_time_value"></a>
##### [`pixel_dwell_time_value`](#pixel_dwell_time_value)
Resident time of primary ion beam on each pixel.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

<a name="pixel_dwell_time_unit"></a>
##### [`pixel_dwell_time_unit`](#pixel_dwell_time_unit)
Pixel dwell time unit. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| enum | `ms` |
| required | `False` |
| required if | `pixel_dwell_time_value` present |

<a name="pixel_size_x_value"></a>
##### [`pixel_size_x_value`](#pixel_size_x_value)
Width value of the pixel or voxel measurement (distinct from the image resolution_x_value).

| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

<a name="pixel_size_x_unit"></a>
##### [`pixel_size_x_unit`](#pixel_size_x_unit)
Width unit of the pixel or voxel measurement. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| enum | `nm` |
| required | `False` |
| required if | `pixel_size_x_value` present |

<a name="pixel_size_y_value"></a>
##### [`pixel_size_y_value`](#pixel_size_y_value)
Length value of the pixel or voxel measurement (distinct from the image resolution_y_value).

| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

<a name="pixel_size_y_unit"></a>
##### [`pixel_size_y_unit`](#pixel_size_y_unit)
Length unit of the pixel or voxel measurement. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| enum | `nm` |
| required | `False` |
| required if | `pixel_size_y_value` present |

<a name="preparation_instrument_vendor"></a>
##### [`preparation_instrument_vendor`](#preparation_instrument_vendor)
The manufacturer of the instrument used to prepare the sample for the assay.

| constraint | value |
| --- | --- |
| enum | `Custom` or `Ionpath` |
| required | `True` |

<a name="preparation_instrument_model"></a>
##### [`preparation_instrument_model`](#preparation_instrument_model)
The model number/name of the instrument used to prepare the sample for the assay.

| constraint | value |
| --- | --- |
| enum | `Custom`, `MIBIscope 1`, or `MIBIscope 2` |
| required | `True` |

<a name="primary_ion"></a>
##### [`primary_ion`](#primary_ion)
Primary ion.

| constraint | value |
| --- | --- |
| enum | `Xe` |
| required | `True` |

<a name="primary_ion_current_value"></a>
##### [`primary_ion_current_value`](#primary_ion_current_value)
Primary ion current value.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

<a name="primary_ion_current_unit"></a>
##### [`primary_ion_current_unit`](#primary_ion_current_unit)
Primary ion current unit, typically nA or pA. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| enum | `nA` or `pA` |
| required | `False` |
| required if | `primary_ion_current_value` present |

<a name="reagent_prep_protocols_io_doi"></a>
##### [`reagent_prep_protocols_io_doi`](#reagent_prep_protocols_io_doi)
DOI for protocols.io referring to the protocol for preparing reagents for the assay.

| constraint | value |
| --- | --- |
| required | `True` |
| pattern (regular expression) | <code>10\.17504/.*</code> |
| url | prefix: <code>https://dx.doi.org/</code> |

<a name="section_prep_protocols_io_doi"></a>
##### [`section_prep_protocols_io_doi`](#section_prep_protocols_io_doi)
DOI for protocols.io referring to the protocol for preparing tissue sections for the assay.

| constraint | value |
| --- | --- |
| required | `True` |
| pattern (regular expression) | <code>10\.17504/.*</code> |
| url | prefix: <code>https://dx.doi.org/</code> |

<a name="segment_data_format"></a>
##### [`segment_data_format`](#segment_data_format)
This refers to the data type, which is a "float" for the IMC counts.

| constraint | value |
| --- | --- |
| enum | `float`, `integer`, or `string` |
| required | `True` |

<a name="signal_type"></a>
##### [`signal_type`](#signal_type)
Type of signal measured per channel (usually dual counts)

| constraint | value |
| --- | --- |
| enum | `dual count`, `pulse count`, or `intensity value` |
| required | `True` |

<a name="start_datetime"></a>
##### [`start_datetime`](#start_datetime)
Time stamp indicating start of ablation for ROI.

| constraint | value |
| --- | --- |
| type | `datetime` |
| format | `%Y-%m-%d %H:%M` |
| required | `True` |

<a name="antibodies_path"></a>
##### [`antibodies_path`](#antibodies_path)
Relative path to file with antibody information for this dataset.

| constraint | value |
| --- | --- |
| required | `True` |

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

