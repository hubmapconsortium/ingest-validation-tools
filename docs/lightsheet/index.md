---
title: Light Sheet
schema_name: lightsheet
category: Imaging assays
all_versions_deprecated: False
exclude_from_index: False
layout: default
---

Related files:
- [🔬 Background doc](https://portal.hubmapconsortium.org/docs/assays/lightsheet): More details about this type.
- [📝 Excel template](https://raw.githubusercontent.com/hubmapconsortium/ingest-validation-tools/main/docs/lightsheet/lightsheet-metadata.xlsx): For metadata entry.
- [📝 TSV template](https://raw.githubusercontent.com/hubmapconsortium/ingest-validation-tools/main/docs/lightsheet/lightsheet-metadata.tsv): Alternative for metadata entry.

Lightsheet uploads require metadata on the antibodies used in the assay to be provided in an Antibodies TSV. For Lightsheet, the `channel_id` is the name of the fluorophore tag on the antibody. For an example of a lightsheet dataset & directory, see this  [example lightsheet dataset](https://portal.hubmapconsortium.org/browse/dataset/b6eba6afe660a8a85c2648e368b0cf9f#files)  and click the Globus link. 
Version 2 has 5 new fields for metadata describing the Z-dimension specifically relevant to lightsheet. These values provide the total number of image sections captured, the incremental value and unit of distance between the sections and the value and unit of the total distance captured.
The other fields function the same way for all assays using antibodies. For more information, see the [Antibodies TSV documentation](../antibodies).

## Directory schemas
### v1

| pattern | required? | description |
| --- | --- | --- |
| <code>Level0/Channel[^/]+/[^/]+\.csv</code> | ✓ | **[QA/QC]** Contains metadata and channel info. |
| <code>Level0/Channel[^/]+/[^/]+\.czi</code> |  | Zeiss raw image file. |
| <code>Level0/merged/Channel[^/]+/[^/]+\.czi</code> |  | Merged Zeiss raw image file. |
| <code>Level0/Channel[^/]+/[^/]+\.ome.tiff</code> | ✓ | Raw image file. |
| <code>Level0/merged/Channel[^/]+/[^/]+\.ome.tiff</code> | ✓ | Merged raw image file. |
| <code>Level1/Channel[^/]+/[^/]+\.tif</code> |  | Stitched image. |
| <code>Level1/merged/Channel[^/]+/[^/]+\.tif</code> |  | Merged stitched image. |
| <code>Level1/Channel[^/]+/[^/]+\.mp4</code> |  | Stitched image. |
| <code>Level2/Channel[^/]+/[^/]+\.csv</code> |  | **[QA/QC]** Contains file, parent and bounds. Required when level 2 is populated. File is optional. |
| <code>Level2/Channel[^/]+/[^/]+\.obj</code> |  | Segmentation mask. |
| <code>Level2/Channel[^/]+/[^/]+\.stl</code> |  | Segmentation mask. |
| <code>Level2/Channel[^/]+/[^/]+\.ome.tiff</code> |  | Segmentation mask. |
| <code>Level2/merged/Channel[^/]+/[^/]+\.ome.tiff</code> |  | Merged segmentation mask. |
| <code>Level3/Channel[^/]+/[^/]+\.csv</code> |  | **[QA/QC]** Contains file, parent and bounds. Required when level 3 is populated. File is optional. |
| <code>Level3/Channel[^/]+/[^/]+\.obj</code> |  | Annotation file. |
| <code>Level3/Channel[^/]+/[^/]+\.stl</code> |  | Annotation file. |
| <code>Level3/Channel[^/]+/[^/]+\.ome.tiff</code> |  | Image file. |
| <code>Level3/merged/Channel[^/]+/[^/]+\.ome.tiff</code> |  | Merged image file. |
| <code>extras/.*</code> |  | Free-form descriptive information supplied by the TMC |

### v0

| pattern | required? | description |
| --- | --- | --- |
| <code>Level0/Channel[^/]+/[^/]+\.csv</code> | ✓ | **[QA/QC]** Contains metadata and channel info. |
| <code>Level0/Channel[^/]+/[^/]+\.czi</code> |  | Zeiss raw image file. File is optional. |
| <code>Level0/Channel[^/]+/[^/]+\.ome.tiff</code> | ✓ | Raw image file. |
| <code>Level1/Channel[^/]+/[^/]+\.tif</code> |  | Stitched image. File is optional. |
| <code>Level1/Channel[^/]+/[^/]+\.mp4</code> |  | Stitched image. File is optional. |
| <code>Level2/Channel[^/]+/[^/]+\.csv</code> |  | **[QA/QC]** Contains file, parent and bounds. Required when level 2 is populated. File is optional. |
| <code>Level2/Channel[^/]+/[^/]+\.obj</code> |  | Segmentation mask. File is optional. |
| <code>Level2/Channel[^/]+/[^/]+\.stl</code> |  | Segmentation mask. File is optional. |
| <code>Level2/Channel[^/]+/[^/]+\.ome.tiff</code> |  | Segmentation mask. File is optional. |
| <code>Level3/Channel[^/]+/[^/]+\.csv</code> |  | **[QA/QC]** Contains file, parent and bounds. Required when level 3 is populated. File is optional. |
| <code>Level3/Channel[^/]+/[^/]+\.obj</code> |  | Annotation file. File is optional. |
| <code>Level3/Channel[^/]+/[^/]+\.stl</code> |  | Annotation file. File is optional. |
| <code>Level3/Channel[^/]+/[^/]+\.ome.tiff</code> |  | Annotation file. File is optional. |
| <code>extras/.*</code> |  | Free-form descriptive information supplied by the TMC |



In the portal: Light Sheet not in Portal

## Metadata schema

### Field types
- *Boolean* fields can be given as `TRUE`/`FALSE`, `True`/`False`, `true`/`false`, or `1`/`0`.  


<details markdown="1" open="true"><summary><b>Version 2 (current)</b></summary>

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

[`resolution_x_value`](#resolution_x_value)<br>
[`resolution_x_unit`](#resolution_x_unit)<br>
[`resolution_y_value`](#resolution_y_value)<br>
[`resolution_y_unit`](#resolution_y_unit)<br>
[`range_z_value`](#range_z_value)<br>
[`range_z_unit`](#range_z_unit)<br>
[`step_z_value`](#step_z_value)<br>
[`increment_z_value`](#increment_z_value)<br>
[`increment_z_unit`](#increment_z_unit)<br>
[`number_of_antibodies`](#number_of_antibodies)<br>
[`number_of_channels`](#number_of_channels)<br>
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
| enum | `2` |
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
| enum | `imaging` |
| required | `True` |

<a name="assay_type"></a>
##### [`assay_type`](#assay_type)
The specific type of assay being executed.

| constraint | value |
| --- | --- |
| enum | `Light Sheet` |
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
| enum | `nm` or `um` |
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
| enum | `nm` or `um` |
| required | `False` |
| required if | `resolution_y_value` present |

<a name="range_z_value"></a>
##### [`range_z_value`](#range_z_value)
The total range of the z axis.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

<a name="range_z_unit"></a>
##### [`range_z_unit`](#range_z_unit)
The unit of range_z_value. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| enum | `nm` or `um` |
| required | `False` |
| required if | `range_z_value` present |

<a name="step_z_value"></a>
##### [`step_z_value`](#step_z_value)
The number of optical sections in z axis range.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

<a name="increment_z_value"></a>
##### [`increment_z_value`](#increment_z_value)
The distance between sequential optical sections.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

<a name="increment_z_unit"></a>
##### [`increment_z_unit`](#increment_z_unit)
The units of increment z value. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| enum | `nm` or `um` |
| required | `False` |
| required if | `increment_z_value` present |

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


<details markdown="1" ><summary><b>Version 1</b></summary>


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
| enum | `imaging` |
| required | `True` |

<a name="assay_type"></a>
##### [`assay_type`](#assay_type)
The specific type of assay being executed.

| constraint | value |
| --- | --- |
| enum | `Light Sheet` |
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
| enum | `nm` or `um` |
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
| enum | `nm` or `um` |
| required | `False` |
| required if | `resolution_y_value` present |

<a name="resolution_z_value"></a>
##### [`resolution_z_value`](#resolution_z_value)
The distance at which two objects along the detection z-axis can be distinguished (resolved as 2 objects).

| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

<a name="resolution_z_unit"></a>
##### [`resolution_z_unit`](#resolution_z_unit)
The unit of distance at which two objects along the detection z-axis can be distinguished (resolved as 2 objects). Leave blank if not applicable.

| constraint | value |
| --- | --- |
| enum | `mm`, `um`, or `nm` |
| required | `False` |
| required if | `resolution_z_value` present |

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



<details markdown="1" ><summary><b>Version 0</b></summary>


### Shared by all types

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
| pattern (regular expression) | <code>([A-Z]+[0-9]+)-[A-Z]{2}\d*(-\d+)+(_\d+)?</code> |
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
| enum | `imaging` |
| required | `True` |

<a name="assay_type"></a>
##### [`assay_type`](#assay_type)
The specific type of assay being executed.

| constraint | value |
| --- | --- |
| enum | `Light Sheet` |
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
| enum | `nm` or `um` |
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
| enum | `nm` or `um` |
| required | `False` |
| required if | `resolution_y_value` present |

<a name="resolution_z_value"></a>
##### [`resolution_z_value`](#resolution_z_value)
The distance at which two objects along the detection z-axis can be distinguished (resolved as 2 objects).

| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

<a name="resolution_z_unit"></a>
##### [`resolution_z_unit`](#resolution_z_unit)
The unit of distance at which two objects along the detection z-axis can be distinguished (resolved as 2 objects). Leave blank if not applicable.

| constraint | value |
| --- | --- |
| enum | `mm`, `um`, or `nm` |
| required | `False` |
| required if | `resolution_z_value` present |

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
