---
title: MALDI-IMS / SIMS-IMS / NanoDESI / DESI
schema_name: ims
category: Imaging mass spectrometry
all_versions_deprecated: False
layout: default
---

Related files:
- [🔬 Background doc](https://portal.hubmapconsortium.org/docs/assays/maldi-ims): More details about this type.
- [📝 Excel template](https://raw.githubusercontent.com/hubmapconsortium/ingest-validation-tools/main/docs/ims/ims-metadata.xlsx): For metadata entry.
- [📝 TSV template](https://raw.githubusercontent.com/hubmapconsortium/ingest-validation-tools/main/docs/ims/ims-metadata.tsv): Alternative for metadata entry.

This schema is for imaging mass spectrometry (IMS).

## Directory schemas
### v0

| pattern | required? | description |
| --- | --- | --- |
| <code>csv/[^/]+\.csv</code> |  | Intensities M/Z values with Pixel location |
| <code>imzML/[^/]+\.ibd</code> | ✓ | Mass spec data saved in a binary format. |
| <code>imzML/[^/]+\.imzML</code> | ✓ | Mass spec metadata saved in XML format. Index to .ibd file. |
| <code>metadata/[^/]+_LipidAssignments\.xlsx</code> |  | Microsoft Excel file containing the m/z, assignment, lipid class, etc. |
| <code>metadata/[^/]+_meta\.json</code> |  | JSON file containing the machine parameters/settings |
| <code>metadata/[^/]+_microscopy\.txt</code> |  | Transformations/map back to autofluorescence microscopy (related) data |
| <code>ometiffs/[^/]+_multilayer\.ome\.tiff</code> | ✓ | Aligned multilayer OME TIFF file of the IMS data |
| <code>ometiffs/separate/[^/]+_mz[^/]+\.ome\.tiff</code> |  | Each file is a different M/Z value. |
| <code>extras/.*</code> |  | Free-form descriptive information supplied by the TMC |



In the portal: MALDI-IMS not in Portal / SIMS-IMS not in Portal / NanoDESI not in Portal / DESI not in Portal

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

[`ms_source`](#ms_source)<br>
[`polarity`](#polarity)<br>
[`mz_range_low_value`](#mz_range_low_value)<br>
[`mz_range_high_value`](#mz_range_high_value)<br>
[`mass_resolving_power`](#mass_resolving_power)<br>
[`mz_resolving_power`](#mz_resolving_power)<br>
[`ion_mobility`](#ion_mobility)<br>
[`ms_scan_mode`](#ms_scan_mode)<br>
[`resolution_x_value`](#resolution_x_value)<br>
[`resolution_x_unit`](#resolution_x_unit)<br>
[`resolution_y_value`](#resolution_y_value)<br>
[`resolution_y_unit`](#resolution_y_unit)<br>
[`preparation_type`](#preparation_type)<br>
[`preparation_instrument_vendor`](#preparation_instrument_vendor)<br>
[`preparation_instrument_model`](#preparation_instrument_model)<br>
[`preparation_maldi_matrix`](#preparation_maldi_matrix)<br>
[`desi_solvent`](#desi_solvent)<br>
[`desi_solvent_flow_rate`](#desi_solvent_flow_rate)<br>
[`desi_solvent_flow_rate_unit`](#desi_solvent_flow_rate_unit)<br>
[`section_prep_protocols_io_doi`](#section_prep_protocols_io_doi)<br>
[`processing_protocols_io_doi`](#processing_protocols_io_doi)<br>
[`overall_protocols_io_doi`](#overall_protocols_io_doi)<br>
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
| enum | `mass_spectrometry_imaging` |
| required | `True` |

<a name="assay_type"></a>
##### [`assay_type`](#assay_type)
The specific type of assay being executed.

| constraint | value |
| --- | --- |
| enum | `MALDI-IMS`, `SIMS-IMS`, `NanoDESI`, or `DESI` |
| required | `True` |

<a name="analyte_class"></a>
##### [`analyte_class`](#analyte_class)
Analytes are the target molecules being measured with the assay.

| constraint | value |
| --- | --- |
| enum | `protein`, `metabolites`, `lipids`, `peptides`, `phosphopeptides`, or `glycans` |
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

<a name="ms_source"></a>
##### [`ms_source`](#ms_source)
The ion source type used for surface sampling (MALDI, MALDI-2, DESI, nanoDESI or SIMS).

| constraint | value |
| --- | --- |
| enum | `MALDI`, `MALDI-2`, `LDI`, `LA`, `SIMS-C60`, `SIMS-H2O`, or `nanoDESI` |
| required | `True` |

<a name="polarity"></a>
##### [`polarity`](#polarity)
The polarity of the mass analysis (positive or negative ion modes)

| constraint | value |
| --- | --- |
| enum | `negative ion mode`, `positive ion mode`, or `negative and positive ion mode` |
| required | `True` |

<a name="mz_range_low_value"></a>
##### [`mz_range_low_value`](#mz_range_low_value)
The low value of the scanned mass range for MS1. (unitless)

| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

<a name="mz_range_high_value"></a>
##### [`mz_range_high_value`](#mz_range_high_value)
The high value of the scanned mass range for MS1. (unitless)

| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

<a name="mass_resolving_power"></a>
##### [`mass_resolving_power`](#mass_resolving_power)
The MS1 resolving power defined as m/∆m where ∆m is the FWHM for a given peak with a specified m/z (m). (unitless)

| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

<a name="mz_resolving_power"></a>
##### [`mz_resolving_power`](#mz_resolving_power)
The peak (m/z) used to calculate the resolving power.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

<a name="ion_mobility"></a>
##### [`ion_mobility`](#ion_mobility)
Specifies whether or not ion mobility spectrometry was performed and which technology was used. Technologies for measuring ion mobility: Traveling Wave Ion Mobility Spectrometry (TWIMS), Trapped Ion Mobility Spectrometry (TIMS), High Field Asymmetric waveform ion Mobility Spectrometry (FAIMS), Drift Tube Ion Mobility Spectrometry (DTIMS, Structures for Lossless Ion Manipulations (SLIM). Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |
| enum | `TIMS`, `TWIMS`, `FAIMS`, `DTIMS`, or `SLIMS` |

<a name="ms_scan_mode"></a>
##### [`ms_scan_mode`](#ms_scan_mode)
Scan mode refers to the number of steps in the separation of fragments.

| constraint | value |
| --- | --- |
| enum | `MS`, `MS/MS`, or `MS3` |
| required | `True` |

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
| units for | `resolution_x_value` |

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
| units for | `resolution_y_value` |

<a name="preparation_type"></a>
##### [`preparation_type`](#preparation_type)
Common methods of depositing matrix for MALDI imaging include robotic spotting, electrospray deposition, and spray-coating with an airbrush. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |

<a name="preparation_instrument_vendor"></a>
##### [`preparation_instrument_vendor`](#preparation_instrument_vendor)
The manufacturer of the instrument used to prepare the sample for the assay. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |

<a name="preparation_instrument_model"></a>
##### [`preparation_instrument_model`](#preparation_instrument_model)
The model number/name of the instrument used to prepare the sample for the assay. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |

<a name="preparation_maldi_matrix"></a>
##### [`preparation_maldi_matrix`](#preparation_maldi_matrix)
The matrix is a compound of crystallized molecules that acts like a buffer between the sample and the laser. It also helps ionize the sample, carrying it along the flight tube so it can be detected. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| enum | `CHB`, `DHB`, or `SA` |
| required | `False` |

<a name="desi_solvent"></a>
##### [`desi_solvent`](#desi_solvent)
Solvent composition for conducting nanospray desorption electrospray ionization (nanoDESI) or desorption electrospray ionization (DESI). Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |

<a name="desi_solvent_flow_rate"></a>
##### [`desi_solvent_flow_rate`](#desi_solvent_flow_rate)
The rate of flow of the solvent into a spray. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `False` |

<a name="desi_solvent_flow_rate_unit"></a>
##### [`desi_solvent_flow_rate_unit`](#desi_solvent_flow_rate_unit)
Units of the rate of solvent flow. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |
| enum | `uL/minute` |
| units for | `desi_solvent_flow_rate` |

<a name="section_prep_protocols_io_doi"></a>
##### [`section_prep_protocols_io_doi`](#section_prep_protocols_io_doi)
DOI for protocols.io referring to the protocol for preparing tissue sections for the assay.

| constraint | value |
| --- | --- |
| required | `True` |
| pattern (regular expression) | <code>10\.17504/.*</code> |
| url | prefix: <code>https://dx.doi.org/</code> |

<a name="processing_protocols_io_doi"></a>
##### [`processing_protocols_io_doi`](#processing_protocols_io_doi)
DOI for analysis protocols.io for this assay. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |
| pattern (regular expression) | <code>10\.17504/.*</code> |
| url | prefix: <code>https://dx.doi.org/</code> |

<a name="overall_protocols_io_doi"></a>
##### [`overall_protocols_io_doi`](#overall_protocols_io_doi)
DOI for protocols.io for the overall process.

| constraint | value |
| --- | --- |
| required | `True` |
| pattern (regular expression) | <code>10\.17504/.*</code> |
| url | prefix: <code>https://dx.doi.org/</code> |

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
| enum | `mass_spectrometry_imaging` |
| required | `True` |

<a name="assay_type"></a>
##### [`assay_type`](#assay_type)
The specific type of assay being executed.

| constraint | value |
| --- | --- |
| enum | `MALDI-IMS` |
| required | `True` |

<a name="analyte_class"></a>
##### [`analyte_class`](#analyte_class)
Analytes are the target molecules being measured with the assay.

| constraint | value |
| --- | --- |
| enum | `protein`, `metabolites`, or `lipids` |
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

<a name="ms_source"></a>
##### [`ms_source`](#ms_source)
The ion source type used for surface sampling (MALDI, MALDI-2, DESI, or SIMS) or LC-MS/MS data acquisition (nESI)

| constraint | value |
| --- | --- |
| enum | `MALDI`, `MALDI-2`, `DESI`, `SIMS`, or `nESI` |
| required | `True` |

<a name="polarity"></a>
##### [`polarity`](#polarity)
The polarity of the mass analysis (positive or negative ion modes)

| constraint | value |
| --- | --- |
| enum | `negative ion mode`, `positive ion mode`, or `negative and positive ion mode` |
| required | `True` |

<a name="mz_range_low_value"></a>
##### [`mz_range_low_value`](#mz_range_low_value)
The low value of the scanned mass range for MS1. (unitless)

| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

<a name="mz_range_high_value"></a>
##### [`mz_range_high_value`](#mz_range_high_value)
The high value of the scanned mass range for MS1. (unitless)

| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

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
| units for | `resolution_x_value` |

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
| units for | `resolution_y_value` |

<a name="preparation_type"></a>
##### [`preparation_type`](#preparation_type)
Common methods of depositing matrix for MALDI imaging include robotic spotting, electrospray deposition, and spray-coating with an airbrush.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="preparation_instrument_vendor"></a>
##### [`preparation_instrument_vendor`](#preparation_instrument_vendor)
The manufacturer of the instrument used to prepare the sample for the assay.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="preparation_instrument_model"></a>
##### [`preparation_instrument_model`](#preparation_instrument_model)
The model number/name of the instrument used to prepare the sample for the assay.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="preparation_maldi_matrix"></a>
##### [`preparation_maldi_matrix`](#preparation_maldi_matrix)
The matrix is a compound of crystallized molecules that acts like a buffer between the sample and the laser. It also helps ionize the sample, carrying it along the flight tube so it can be detected.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="section_prep_protocols_io_doi"></a>
##### [`section_prep_protocols_io_doi`](#section_prep_protocols_io_doi)
DOI for protocols.io referring to the protocol for preparing tissue sections for the assay.

| constraint | value |
| --- | --- |
| required | `True` |
| pattern (regular expression) | <code>10\.17504/.*</code> |
| url | prefix: <code>https://dx.doi.org/</code> |

<a name="overall_protocols_io_doi"></a>
##### [`overall_protocols_io_doi`](#overall_protocols_io_doi)
DOI for protocols.io for the overall process.

| constraint | value |
| --- | --- |
| required | `True` |
| pattern (regular expression) | <code>10\.17504/.*</code> |
| url | prefix: <code>https://dx.doi.org/</code> |

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
| enum | `mass_spectrometry_imaging` |
| required | `True` |

<a name="assay_type"></a>
##### [`assay_type`](#assay_type)
The specific type of assay being executed.

| constraint | value |
| --- | --- |
| enum | `MALDI-IMS` |
| required | `True` |

<a name="analyte_class"></a>
##### [`analyte_class`](#analyte_class)
Analytes are the target molecules being measured with the assay.

| constraint | value |
| --- | --- |
| enum | `protein`, `metabolites`, or `lipids` |
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

<a name="ms_source"></a>
##### [`ms_source`](#ms_source)
The ion source type used for surface sampling (MALDI, MALDI-2, DESI, or SIMS) or LC-MS/MS data acquisition (nESI)

| constraint | value |
| --- | --- |
| enum | `MALDI`, `MALDI-2`, `DESI`, `SIMS`, or `nESI` |
| required | `True` |

<a name="polarity"></a>
##### [`polarity`](#polarity)
The polarity of the mass analysis (positive or negative ion modes)

| constraint | value |
| --- | --- |
| enum | `negative ion mode`, `positive ion mode`, or `negative and positive ion mode` |
| required | `True` |

<a name="mz_range_low_value"></a>
##### [`mz_range_low_value`](#mz_range_low_value)
The low value of the scanned mass range for MS1. (unitless)

| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

<a name="mz_range_high_value"></a>
##### [`mz_range_high_value`](#mz_range_high_value)
The high value of the scanned mass range for MS1. (unitless)

| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

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
| units for | `resolution_x_value` |

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
| units for | `resolution_y_value` |

<a name="preparation_type"></a>
##### [`preparation_type`](#preparation_type)
Common methods of depositing matrix for MALDI imaging include robotic spotting, electrospray deposition, and spray-coating with an airbrush.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="preparation_instrument_vendor"></a>
##### [`preparation_instrument_vendor`](#preparation_instrument_vendor)
The manufacturer of the instrument used to prepare the sample for the assay.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="preparation_instrument_model"></a>
##### [`preparation_instrument_model`](#preparation_instrument_model)
The model number/name of the instrument used to prepare the sample for the assay.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="preparation_maldi_matrix"></a>
##### [`preparation_maldi_matrix`](#preparation_maldi_matrix)
The matrix is a compound of crystallized molecules that acts like a buffer between the sample and the laser. It also helps ionize the sample, carrying it along the flight tube so it can be detected.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="section_prep_protocols_io_doi"></a>
##### [`section_prep_protocols_io_doi`](#section_prep_protocols_io_doi)
DOI for protocols.io referring to the protocol for preparing tissue sections for the assay.

| constraint | value |
| --- | --- |
| required | `True` |
| pattern (regular expression) | <code>10\.17504/.*</code> |
| url | prefix: <code>https://dx.doi.org/</code> |

<a name="overall_protocols_io_doi"></a>
##### [`overall_protocols_io_doi`](#overall_protocols_io_doi)
DOI for protocols.io for the overall process.

| constraint | value |
| --- | --- |
| required | `True` |
| pattern (regular expression) | <code>10\.17504/.*</code> |
| url | prefix: <code>https://dx.doi.org/</code> |

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
