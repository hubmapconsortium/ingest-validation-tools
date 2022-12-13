---
title: CODEX / CODEX2
schema_name: codex
category: Imaging assays
all_versions_deprecated: False
exclude_from_index: False
layout: default
---

Related files:
- [🔬 Background doc](https://portal.hubmapconsortium.org/docs/assays/codex): More details about this type.
- [📝 Excel template](https://raw.githubusercontent.com/hubmapconsortium/ingest-validation-tools/main/docs/codex/codex-metadata.xlsx): For metadata entry.
- [📝 TSV template](https://raw.githubusercontent.com/hubmapconsortium/ingest-validation-tools/main/docs/codex/codex-metadata.tsv): Alternative for metadata entry.

This schema is for CO-Detection by indEXing (CODEX). CODEX uploads require metadata on the antibodies used in the assay to be provided in an Antibodies TSV. For CODEX, in that TSV, the `channel_id` is a cycle#/channel# combination linked to a given image file (of the form `Cycle[0-9]_CH[0-9]`). Each TIF file in a CODEX dataset contains image data captured from a single channel in a single cycle, identified and connected to the `channel_id` by its location in the upload directory (of the form `src_*/cyc*_reg*_*/*_*_Z*_CH*.tif`). For an example of a CODEX dataset & directory, see this example  [CODEX dataset](https://portal.hubmapconsortium.org/browse/dataset/053544cd63125fc25f6a71a8f444bafc#files) and click the Globus link.
The other fields function the same way for all assays using antibodies. For more information, see the [Antibodies TSV documentation](../antibodies).

## Directory schemas
### v1-with-dataset-json

| pattern | required? | description |
| --- | --- | --- |
| <code>[^/]*NAV[^/]*\.tif</code> (example: <code>NAV.tif</code>) |  | Navigational Image showing Region of Interest (Keyance Microscope only) |
| <code>[^/]*\.pdf</code> (example: <code>summary.pdf</code>) |  | **[QA/QC]** PDF export of Powerpoint slide deck containing the Image Analysis Report |
| <code>(raw&#124;processed)/config\.txt&#124;(src_[^/]*&#124;drv_[^/]*&#124;extras)/[sS]egmentation\.json</code> |  | Sanity check that verifies the existence of at least one of these files. This is required for the HuBMAP processing pipeline |
| <code>raw/reg_[^/]*\.png</code> (example: <code>raw/reg_00.png</code>) |  | Region overviews |
| <code>(raw&#124;src_[^/]*)/[Ee]xperiment\.json</code> |  | JSON file produced by the Akoya software which contains the metadata for the experiment, including the software version used, microscope parameters, channel names, pixel dimensions, etc. (required for HuBMAP pipeline) |
| <code>(raw&#124;src_[^/]*)/dataset\.json</code> (example: <code>raw/dataset.json</code>) | ✓ | Additional CODEX specific metadata file |
| <code>processed/HandE\.tif</code> |  | HandE image |
| <code>processed/HandE_RGB\.tif</code> |  | HandE RGB image |
| <code>processed/HandE_RGB_thumbnail.jpg</code> |  | HandE RGB thumbnail |
| <code>(raw&#124;processed)/config\.txt</code> |  | Configuration file with information needed for the HuBMAP processing pipeline |
| <code>(raw&#124;src_.*)/[cC]yc.*_reg.*/.*_Z.*_CH.*\.tif</code> | ✓ | TIFF files produced by the experiment. General folder format: Cycle(n)_Region(n)_date; General file format: name_tileNumber(n)_zplaneNumber(n)_channelNumber(n) |
| <code>src_.*/cyc.*_reg.*_.*/.*\.gci</code> |  | Group Capture Information File (Keyance Microscope only) |
| <code>(raw&#124;src_.*)/.*</code> | ✓ | Raw data directory. |
| <code>(processed&#124;drv_[^/]*)/.*</code> | ✓ | Processed files produced by the Akoya software or alternative software. |
| <code>extras/dir-schema-v1-with-dataset-json</code> | ✓ | Empty file whose presence indicates the version of the directory schema in use |
| <code>extras/.*</code> |  | Free-form descriptive information supplied by the TMC |

### v0

| pattern | required? | description |
| --- | --- | --- |
| <code>[^/]*NAV[^/]*\.tif</code> (example: <code>NAV.tif</code>) |  | Navigational Image showing Region of Interest (Keyance Microscope only) |
| <code>[^/]*\.pdf</code> (example: <code>summary.pdf</code>) |  | **[QA/QC]** PDF export of Powerpoint slide deck containing the Image Analysis Report |
| <code>(raw&#124;processed)/config\.txt&#124;(src_[^/]*&#124;drv_[^/]*)/[sS]egmentation\.json</code> | ✓ | Sanity check that verifies the existence of at least one of these files. This is required for the HuBMAP processing pipeline |
| <code>raw/reg_[^/]*\.png</code> (example: <code>raw/reg_00.png</code>) |  | Region overviews |
| <code>(raw&#124;src_[^/]*)/[Ee]xperiment\.json</code> | ✓ | JSON file produced by the Akoya software which contains the metadata for the experiment, including the software version used, microscope parameters, channel names, pixel dimensions, etc. (required for HuBMAP pipeline) |
| <code>processed/HandE\.tif</code> |  | HandE image |
| <code>processed/HandE_RGB\.tif</code> |  | HandE RGB image |
| <code>processed/HandE_RGB_thumbnail.jpg</code> |  | HandE RGB thumbnail |
| <code>(raw&#124;processed)/config\.txt</code> |  | Configuration file with information needed for the HuBMAP processing pipeline |
| <code>(raw&#124;src_.*)/[cC]yc.*_reg.*/.*_Z.*_CH.*\.tif</code> | ✓ | TIFF files produced by the experiment. General folder format: Cycle(n)_Region(n)_date; General file format: name_tileNumber(n)_zplaneNumber(n)_channelNumber(n) |
| <code>src_.*/cyc.*_reg.*_.*/.*\.gci</code> |  | Group Capture Information File (Keyance Microscope only) |
| <code>(raw&#124;src_.*)/.*</code> | ✓ | Raw data directory. |
| <code>(processed&#124;drv_[^/]*)/.*</code> | ✓ | Processed files produced by the Akoya software or alternative software. |
| <code>extras/.*</code> |  | Free-form descriptive information supplied by the TMC |



In the portal: CODEX not in Portal / CODEX2 not in Portal

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

[`resolution_x_value`](#resolution_x_value)<br>
[`resolution_x_unit`](#resolution_x_unit)<br>
[`resolution_y_value`](#resolution_y_value)<br>
[`resolution_y_unit`](#resolution_y_unit)<br>
[`resolution_z_value`](#resolution_z_value)<br>
[`resolution_z_unit`](#resolution_z_unit)<br>
[`preparation_instrument_vendor`](#preparation_instrument_vendor)<br>
[`preparation_instrument_model`](#preparation_instrument_model)<br>
[`number_of_antibodies`](#number_of_antibodies)<br>
[`number_of_channels`](#number_of_channels)<br>
[`number_of_cycles`](#number_of_cycles)<br>
[`section_prep_protocols_io_doi`](#section_prep_protocols_io_doi)<br>
[`reagent_prep_protocols_io_doi`](#reagent_prep_protocols_io_doi)<br>
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
| enum | `imaging` |
| required | `True` |

<a name="assay_type"></a>
##### [`assay_type`](#assay_type)
The specific type of assay being executed.

| constraint | value |
| --- | --- |
| enum | `CODEX` or `CODEX2` |
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
An acquisition_instrument is the device that contains the signal detection hardware and signal processing software. Assays generate signals such as light of various intensities or color or signals representing molecular mass.

| constraint | value |
| --- | --- |
| enum | `Keyence` or `Zeiss` |
| required | `True` |

<a name="acquisition_instrument_model"></a>
##### [`acquisition_instrument_model`](#acquisition_instrument_model)
Manufacturers of an acquisition instrument may offer various versions (models) of that instrument with different features or sensitivities. Differences in features or sensitivities may be relevant to processing or interpretation of the data.

| constraint | value |
| --- | --- |
| enum | `BZ-X800`, `BZ-X710`, or `Axio Observer Z1` |
| required | `True` |

### Unique to this type

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

<a name="resolution_z_value"></a>
##### [`resolution_z_value`](#resolution_z_value)
Optional if assay does not have multiple z-levels. Note that this is resolution within a given sample: z-pitch (resolution_z_value) is the increment distance between image slices (for Akoya, z-pitch=1.5um) ie. the microscope stage is moved up or down in increments of 1.5um to capture images of several focal planes. The best one will be used & the rest discarded. The thickness of the sample itself is sample metadata. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `False` |

<a name="resolution_z_unit"></a>
##### [`resolution_z_unit`](#resolution_z_unit)
The unit of incremental distance between image slices. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| enum | `mm`, `um`, or `nm` |
| required | `False` |
| required if | `resolution_z_value` present |

<a name="preparation_instrument_vendor"></a>
##### [`preparation_instrument_vendor`](#preparation_instrument_vendor)
The manufacturer of the instrument used to prepare the sample for the assay.

| constraint | value |
| --- | --- |
| enum | `CODEX` |
| required | `True` |

<a name="preparation_instrument_model"></a>
##### [`preparation_instrument_model`](#preparation_instrument_model)
The model number/name of the instrument used to prepare the sample for the assay.

| constraint | value |
| --- | --- |
| enum | `version 1 robot` or `prototype robot - Stanford/Nolan Lab` |
| required | `True` |

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

<a name="number_of_cycles"></a>
##### [`number_of_cycles`](#number_of_cycles)
Number of cycles of 1. oligo application, 2. fluor application, 3. washes.

| constraint | value |
| --- | --- |
| type | `integer` |
| required | `True` |

<a name="section_prep_protocols_io_doi"></a>
##### [`section_prep_protocols_io_doi`](#section_prep_protocols_io_doi)
DOI for protocols.io referring to the protocol for preparing tissue sections for the assay.

| constraint | value |
| --- | --- |
| required | `True` |
| pattern (regular expression) | <code>10\.17504/.*</code> |
| url | prefix: <code>https://dx.doi.org/</code> |

<a name="reagent_prep_protocols_io_doi"></a>
##### [`reagent_prep_protocols_io_doi`](#reagent_prep_protocols_io_doi)
DOI for protocols.io referring to the protocol for preparing reagents for the assay.

| constraint | value |
| --- | --- |
| required | `True` |
| pattern (regular expression) | <code>10\.17504/.*</code> |
| url | prefix: <code>https://dx.doi.org/</code> |

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
| enum | `CODEX` |
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
An acquisition_instrument is the device that contains the signal detection hardware and signal processing software. Assays generate signals such as light of various intensities or color or signals representing molecular mass.

| constraint | value |
| --- | --- |
| enum | `Keyence` or `Zeiss` |
| required | `True` |

<a name="acquisition_instrument_model"></a>
##### [`acquisition_instrument_model`](#acquisition_instrument_model)
Manufacturers of an acquisition instrument may offer various versions (models) of that instrument with different features or sensitivities. Differences in features or sensitivities may be relevant to processing or interpretation of the data.

| constraint | value |
| --- | --- |
| enum | `BZ-X800`, `BZ-X710`, or `Axio Observer Z1` |
| required | `True` |

### Unique to this type

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

<a name="resolution_z_value"></a>
##### [`resolution_z_value`](#resolution_z_value)
Optional if assay does not have multiple z-levels. Note that this is resolution within a given sample: z-pitch (resolution_z_value) is the increment distance between image slices (for Akoya, z-pitch=1.5um) ie. the microscope stage is moved up or down in increments of 1.5um to capture images of several focal planes. The best one will be used & the rest discarded. The thickness of the sample itself is sample metadata. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `False` |

<a name="resolution_z_unit"></a>
##### [`resolution_z_unit`](#resolution_z_unit)
The unit of incremental distance between image slices. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| enum | `mm`, `um`, or `nm` |
| required | `False` |
| required if | `resolution_z_value` present |

### Level 3

<a name="preparation_instrument_vendor"></a>
##### [`preparation_instrument_vendor`](#preparation_instrument_vendor)
The manufacturer of the instrument used to prepare the sample for the assay.

| constraint | value |
| --- | --- |
| enum | `CODEX` |
| required | `True` |

<a name="preparation_instrument_model"></a>
##### [`preparation_instrument_model`](#preparation_instrument_model)
The model number/name of the instrument used to prepare the sample for the assay.

| constraint | value |
| --- | --- |
| enum | `version 1 robot` or `prototype robot - Stanford/Nolan Lab` |
| required | `True` |

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

<a name="number_of_cycles"></a>
##### [`number_of_cycles`](#number_of_cycles)
Number of cycles of 1. oligo application, 2. fluor application, 3. washes.

| constraint | value |
| --- | --- |
| type | `integer` |
| required | `True` |

<a name="section_prep_protocols_io_doi"></a>
##### [`section_prep_protocols_io_doi`](#section_prep_protocols_io_doi)
DOI for protocols.io referring to the protocol for preparing tissue sections for the assay.

| constraint | value |
| --- | --- |
| required | `True` |
| pattern (regular expression) | <code>10\.17504/.*</code> |
| url | prefix: <code>https://dx.doi.org/</code> |

<a name="reagent_prep_protocols_io_doi"></a>
##### [`reagent_prep_protocols_io_doi`](#reagent_prep_protocols_io_doi)
DOI for protocols.io referring to the protocol for preparing reagents for the assay.

| constraint | value |
| --- | --- |
| required | `True` |
| pattern (regular expression) | <code>10\.17504/.*</code> |
| url | prefix: <code>https://dx.doi.org/</code> |

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
