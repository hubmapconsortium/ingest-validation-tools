---
title: LC-MS / MS / LC-MS Bottom-Up / MS Bottom-Up / LC-MS Top-Down / MS Top-Down
schema_name: lcms
category: Mass spectrometry
all_versions_deprecated: False
layout: default
---

Related files:
- [🔬 Background doc](https://portal.hubmapconsortium.org/docs/assays/lcms): More details about this type.
- [📝 Excel template](https://raw.githubusercontent.com/hubmapconsortium/ingest-validation-tools/main/docs/lcms/lcms-metadata.xlsx): For metadata entry.
- [📝 TSV template](https://raw.githubusercontent.com/hubmapconsortium/ingest-validation-tools/main/docs/lcms/lcms-metadata.tsv): Alternative for metadata entry.

This schema is for liquid chromatography mass spectrometry (LCMS). v2 adds `mass_resolving_power`, `mz_resolving_power`, `ion_mobility`, `spatial_type`, `spatial_sampling_type`, `spatial_target`, and `resolution_{x/y}_{value/unit}`. In the case of datasets in which more than one `analyte_type` was interrogated (e.g. lipids plus metabolytes), those datasets should be split into one dataset per analyte. For an example of an LC-MS dataset & directory, see this [example LC-MS dataset](https://portal.hubmapconsortium.org/browse/dataset/7f1fd7b9c8c3745fcab037a2fa37f5b9) and click the Globus link.

## Directory schema

| pattern | required? | description |
| --- | --- | --- |
| `raw_data/*\.(raw\|mzML)` | ✓ | Raw mass spectrometry data from an assay of LC-MS, MS, LC-MS Bottom-Up, MS Bottom-Up, LC-MS Top-Down, or MS Top-Down that describes an analyte class of protein, metabolites, lipids, peptides, phosphopeptides, or glycans. |
| `ID_search_results/*\.(txt\|csv)` | ✓ | Identification results. Annotated data describing (qualitative or quantitative) the proteins, metabolites, lipids, peptides, phosphopeptides, or glycans identified from the corresponding raw data. |
| `ID_metadata/*\.xml` |  | Identification search parameters / metadata. Software settings used during the analyte identification process (e.g., from MaxQuant or Proteome Discoverer). |
| `QC_results/*\.(xml\|txt\|html\|pdf\|log\|yaml)` |  | Output file resulting from QC analysis. A list of metrics with the score of the current dataset that shows the quality of data collection. |
| `extras/.*` |  | Free-form descriptive information supplied by the TMC |
| `extras/thumbnail\.(png\|jpg)` |  | Optional thumbnail image which may be shown in search interface |

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

</details>
<details markdown="1"><summary>Unique to this type</summary>

[`acquisition_instrument_vendor`](#acquisition_instrument_vendor)<br>
[`acquisition_instrument_model`](#acquisition_instrument_model)<br>
[`ms_source`](#ms_source)<br>
[`polarity`](#polarity)<br>
[`mz_range_low_value`](#mz_range_low_value)<br>
[`mz_range_high_value`](#mz_range_high_value)<br>
[`mass_resolving_power`](#mass_resolving_power)<br>
[`mz_resolving_power`](#mz_resolving_power)<br>
[`ion_mobility`](#ion_mobility)<br>
[`data_collection_mode`](#data_collection_mode)<br>
[`ms_scan_mode`](#ms_scan_mode)<br>
[`labeling`](#labeling)<br>
[`section_prep_protocols_io_doi`](#section_prep_protocols_io_doi)<br>
[`lc_instrument_vendor`](#lc_instrument_vendor)<br>
[`lc_instrument_model`](#lc_instrument_model)<br>
[`lc_column_vendor`](#lc_column_vendor)<br>
[`lc_column_model`](#lc_column_model)<br>
[`lc_resin`](#lc_resin)<br>
[`lc_length_value`](#lc_length_value)<br>
[`lc_length_unit`](#lc_length_unit)<br>
[`lc_temp_value`](#lc_temp_value)<br>
[`lc_temp_unit`](#lc_temp_unit)<br>
[`lc_id_value`](#lc_id_value)<br>
[`lc_id_unit`](#lc_id_unit)<br>
[`lc_flow_rate_value`](#lc_flow_rate_value)<br>
[`lc_flow_rate_unit`](#lc_flow_rate_unit)<br>
[`lc_gradient`](#lc_gradient)<br>
[`lc_mobile_phase_a`](#lc_mobile_phase_a)<br>
[`lc_mobile_phase_b`](#lc_mobile_phase_b)<br>
[`spatial_type`](#spatial_type)<br>
[`spatial_sampling_type`](#spatial_sampling_type)<br>
[`spatial_target`](#spatial_target)<br>
[`resolution_x_value`](#resolution_x_value)<br>
[`resolution_x_unit`](#resolution_x_unit)<br>
[`resolution_y_value`](#resolution_y_value)<br>
[`resolution_y_unit`](#resolution_y_unit)<br>
[`processing_search`](#processing_search)<br>
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
| pattern (regular expression) | `[A-Z]+[0-9]+` |
| required | `True` |

<a name="tissue_id"></a>
##### [`tissue_id`](#tissue_id)
HuBMAP Display ID of the assayed tissue. Example: `ABC123-BL-1-2-3_456`.

| constraint | value |
| --- | --- |
| pattern (regular expression) | `([A-Z]+[0-9]+)-[A-Z]{2}\d*(-\d+)+(_\d+)?` |
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
| pattern (regular expression) | `10\.17504/.*` |
| url | prefix: `https://dx.doi.org/` |

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
| enum | `mass_spectrometry` |
| required | `True` |

<a name="assay_type"></a>
##### [`assay_type`](#assay_type)
Bottom-up refers to analyzing proteins in a sample by digesting them to peptides. Top-down refers to analyzing whole proteins without digestion. LC-MS and MS are for lipids/metabolites. LC-MS Bottom-Up and MS Bottom-Up are for peptides. LC-MS Top-Down and MS Top-Down are for proteins.

| constraint | value |
| --- | --- |
| enum | `LC-MS`, `MS`, `LC-MS Bottom-Up`, `MS Bottom-Up`, `LC-MS Top-Down`, or `MS Top-Down` |
| required | `True` |

<a name="analyte_class"></a>
##### [`analyte_class`](#analyte_class)
Analytes are the target molecules being measured with the assay. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| enum | `protein`, `metabolites`, `lipids`, `peptides`, `phosphopeptides`, or `glycans` |
| required | `False` |

<a name="is_targeted"></a>
##### [`is_targeted`](#is_targeted)
Specifies whether or not a specific molecule(s) is/are targeted for detection/measurement by the assay.

| constraint | value |
| --- | --- |
| type | `boolean` |
| required | `True` |

### Unique to this type

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

<a name="ms_source"></a>
##### [`ms_source`](#ms_source)
The ion source type used for surface sampling.

| constraint | value |
| --- | --- |
| enum | `ESI` |
| required | `True` |

<a name="polarity"></a>
##### [`polarity`](#polarity)
The polarity of the mass analysis (positive or negative ion modes)

| constraint | value |
| --- | --- |
| enum | `negative ion mode` or `positive ion mode` |
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
The MS1 resolving power defined as m/∆m where ∆m is the FWHM for a given peak with a specified m/z (m). (unitless) Leave blank if not applicable.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `False` |

<a name="mz_resolving_power"></a>
##### [`mz_resolving_power`](#mz_resolving_power)
The peak (m/z) used to calculate the resolving power. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `False` |

<a name="ion_mobility"></a>
##### [`ion_mobility`](#ion_mobility)
Specifies whether or not ion mobility spectrometry was performed and which technology was used. Technologies for measuring ion mobility: Traveling Wave Ion Mobility Spectrometry (TWIMS), Trapped Ion Mobility Spectrometry (TIMS), High Field Asymmetric waveform ion Mobility Spectrometry (FAIMS), Drift Tube Ion Mobility Spectrometry (DTIMS, Structures for Lossless Ion Manipulations (SLIM). Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |
| enum | `TIMS`, `TWIMS`, `FAIMS`, `DTIMS`, or `SLIMS` |

<a name="data_collection_mode"></a>
##### [`data_collection_mode`](#data_collection_mode)
Mode of data collection in tandem MS assays. Either DDA (Data-dependent acquisition) or DIA (Data-independent acquisition).

| constraint | value |
| --- | --- |
| required | `True` |

<a name="ms_scan_mode"></a>
##### [`ms_scan_mode`](#ms_scan_mode)
Indicates whether experiment is MS, MS/MS, or other (possibly MS3 for TMT)

| constraint | value |
| --- | --- |
| required | `True` |

<a name="labeling"></a>
##### [`labeling`](#labeling)
Indicates whether samples were labeled prior to MS analysis (e.g., TMT)

| constraint | value |
| --- | --- |
| required | `True` |

<a name="section_prep_protocols_io_doi"></a>
##### [`section_prep_protocols_io_doi`](#section_prep_protocols_io_doi)
DOI for protocols.io referring to the protocol for preparing tissue sections for the assay.

| constraint | value |
| --- | --- |
| required | `True` |
| pattern (regular expression) | `10\.17504/.*` |
| url | prefix: `https://dx.doi.org/` |

<a name="lc_instrument_vendor"></a>
##### [`lc_instrument_vendor`](#lc_instrument_vendor)
The manufacturer of the instrument used for LC. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |

<a name="lc_instrument_model"></a>
##### [`lc_instrument_model`](#lc_instrument_model)
The model number/name of the instrument used for LC. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |

<a name="lc_column_vendor"></a>
##### [`lc_column_vendor`](#lc_column_vendor)
OPTIONAL: The manufacturer of the LC Column unless self-packed, pulled tip capilary is used. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |

<a name="lc_column_model"></a>
##### [`lc_column_model`](#lc_column_model)
The model number/name of the LC Column - IF custom self-packed, pulled tip calillary is used enter "Pulled tip capilary". Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |

<a name="lc_resin"></a>
##### [`lc_resin`](#lc_resin)
Details of the resin used for lc, including vendor, particle size, pore size. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |

<a name="lc_length_value"></a>
##### [`lc_length_value`](#lc_length_value)
LC column length. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `False` |

<a name="lc_length_unit"></a>
##### [`lc_length_unit`](#lc_length_unit)
units for LC column length (typically cm) Leave blank if not applicable.

| constraint | value |
| --- | --- |
| enum | `um`, `mm`, or `cm` |
| required | `False` |
| units for | `lc_length_value` |

<a name="lc_temp_value"></a>
##### [`lc_temp_value`](#lc_temp_value)
LC temperature. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `False` |

<a name="lc_temp_unit"></a>
##### [`lc_temp_unit`](#lc_temp_unit)
units for LC temperature. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| enum | `C` |
| required | `False` |
| units for | `lc_temp_value` |

<a name="lc_id_value"></a>
##### [`lc_id_value`](#lc_id_value)
LC column inner diameter (microns) Leave blank if not applicable.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `False` |

<a name="lc_id_unit"></a>
##### [`lc_id_unit`](#lc_id_unit)
units of LC column inner diameter (typically microns) Leave blank if not applicable.

| constraint | value |
| --- | --- |
| enum | `um`, `mm`, or `cm` |
| required | `False` |
| units for | `lc_id_value` |

<a name="lc_flow_rate_value"></a>
##### [`lc_flow_rate_value`](#lc_flow_rate_value)
Value of flow rate. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `False` |

<a name="lc_flow_rate_unit"></a>
##### [`lc_flow_rate_unit`](#lc_flow_rate_unit)
Units of flow rate. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |
| enum | `nL/min` or `mL/min` |
| units for | `lc_flow_rate_value` |

<a name="lc_gradient"></a>
##### [`lc_gradient`](#lc_gradient)
LC gradient. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |

<a name="lc_mobile_phase_a"></a>
##### [`lc_mobile_phase_a`](#lc_mobile_phase_a)
Composition of mobile phase A. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |

<a name="lc_mobile_phase_b"></a>
##### [`lc_mobile_phase_b`](#lc_mobile_phase_b)
Composition of mobile phase B. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |

<a name="spatial_type"></a>
##### [`spatial_type`](#spatial_type)
Specifies whether or not the analysis was performed in a spatialy targeted manner and the technique used for spatial sampling. For example, Laser-capture microdissection (LCM), Liquid Extraction Surface Analysis (LESA), Nanodroplet Processing in One pot for Trace Samples (nanoPOTS). Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |
| enum | `LCM`, `LESA`, `nanoPOTS`, or `microLESA` |

<a name="spatial_sampling_type"></a>
##### [`spatial_sampling_type`](#spatial_sampling_type)
Specifies whether or not the analysis was performed in a spatially targeted manner. Spatial profiling experiments target specific tissue foci but do not necessarily generate images. Spatial imaging expriments collect data from a regular array (pixels) that can be visualized as heat maps of ion intensity at each location (molecular images). Leave blank if data are derived from bulk analysis. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |
| enum | `profiling` or `imaging` |

<a name="spatial_target"></a>
##### [`spatial_target`](#spatial_target)
Specifies the cell-type or functional tissue unit (FTU) that is targeted in the spatial profiling experiment. Leave blank if data are generated in imaging mode without a specific target structure. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |

<a name="resolution_x_value"></a>
##### [`resolution_x_value`](#resolution_x_value)
The width of a pixel. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `False` |

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
The height of a pixel. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `False` |

<a name="resolution_y_unit"></a>
##### [`resolution_y_unit`](#resolution_y_unit)
The unit of measurement of the height of a pixel. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| enum | `nm` or `um` |
| required | `False` |
| units for | `resolution_y_value` |

<a name="processing_search"></a>
##### [`processing_search`](#processing_search)
Software for analyzing and searching LC-MS/MS omics data.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="processing_protocols_io_doi"></a>
##### [`processing_protocols_io_doi`](#processing_protocols_io_doi)
DOI for analysis protocols.io for this assay. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |
| pattern (regular expression) | `10\.17504/.*` |
| url | prefix: `https://dx.doi.org/` |

<a name="overall_protocols_io_doi"></a>
##### [`overall_protocols_io_doi`](#overall_protocols_io_doi)
DOI for protocols.io for the overall process for this assay. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |
| pattern (regular expression) | `10\.17504/.*` |
| url | prefix: `https://dx.doi.org/` |

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
| pattern (regular expression) | `[A-Z]+[0-9]+` |
| required | `True` |

<a name="tissue_id"></a>
##### [`tissue_id`](#tissue_id)
HuBMAP Display ID of the assayed tissue. Example: `ABC123-BL-1-2-3_456`.

| constraint | value |
| --- | --- |
| pattern (regular expression) | `([A-Z]+[0-9]+)-[A-Z]{2}\d*(-\d+)+(_\d+)?` |
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
| pattern (regular expression) | `10\.17504/.*` |
| url | prefix: `https://dx.doi.org/` |

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
| enum | `mass_spectrometry` |
| required | `True` |

<a name="assay_type"></a>
##### [`assay_type`](#assay_type)
The specific type of assay being executed.

| constraint | value |
| --- | --- |
| enum | `LC-MS (metabolomics)`, `LC-MS/MS (label-free proteomics)`, or `MS (shotgun lipidomics)` |
| required | `True` |

<a name="analyte_class"></a>
##### [`analyte_class`](#analyte_class)
Analytes are the target molecules being measured with the assay. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| enum | `protein`, `metabolites`, or `lipids` |
| required | `False` |

<a name="is_targeted"></a>
##### [`is_targeted`](#is_targeted)
Specifies whether or not a specific molecule(s) is/are targeted for detection/measurement by the assay.

| constraint | value |
| --- | --- |
| type | `boolean` |
| required | `True` |

### Unique to this type

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

<a name="ms_source"></a>
##### [`ms_source`](#ms_source)
The ion source type used for surface sampling (MALDI, MALDI-2, DESI, or SIMS) or LC-MS/MS data acquisition (nESI)

| constraint | value |
| --- | --- |
| required | `True` |

<a name="polarity"></a>
##### [`polarity`](#polarity)
The polarity of the mass analysis (positive or negative ion modes)

| constraint | value |
| --- | --- |
| enum | `negative ion mode` or `positive ion mode` |
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

<a name="data_collection_mode"></a>
##### [`data_collection_mode`](#data_collection_mode)
Mode of data collection in tandem MS assays. Either DDA (Data-dependent acquisition) or DIA (Data-independent acquisition).

| constraint | value |
| --- | --- |
| required | `True` |

<a name="ms_scan_mode"></a>
##### [`ms_scan_mode`](#ms_scan_mode)
Indicates whether experiment is MS, MS/MS, or other (possibly MS3 for TMT)

| constraint | value |
| --- | --- |
| required | `True` |

<a name="labeling"></a>
##### [`labeling`](#labeling)
Indicates whether samples were labeled prior to MS analysis (e.g., TMT)

| constraint | value |
| --- | --- |
| required | `True` |

<a name="section_prep_protocols_io_doi"></a>
##### [`section_prep_protocols_io_doi`](#section_prep_protocols_io_doi)
DOI for protocols.io referring to the protocol for preparing tissue sections for the assay.

| constraint | value |
| --- | --- |
| required | `True` |
| pattern (regular expression) | `10\.17504/.*` |
| url | prefix: `https://dx.doi.org/` |

<a name="lc_instrument_vendor"></a>
##### [`lc_instrument_vendor`](#lc_instrument_vendor)
The manufacturer of the instrument used for LC. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |

<a name="lc_instrument_model"></a>
##### [`lc_instrument_model`](#lc_instrument_model)
The model number/name of the instrument used for LC. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |

<a name="lc_column_vendor"></a>
##### [`lc_column_vendor`](#lc_column_vendor)
OPTIONAL: The manufacturer of the LC Column unless self-packed, pulled tip capilary is used. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |

<a name="lc_column_model"></a>
##### [`lc_column_model`](#lc_column_model)
The model number/name of the LC Column - IF custom self-packed, pulled tip calillary is used enter "Pulled tip capilary". Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |

<a name="lc_resin"></a>
##### [`lc_resin`](#lc_resin)
Details of the resin used for lc, including vendor, particle size, pore size. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |

<a name="lc_length_value"></a>
##### [`lc_length_value`](#lc_length_value)
LC column length. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `False` |

<a name="lc_length_unit"></a>
##### [`lc_length_unit`](#lc_length_unit)
units for LC column length (typically cm) Leave blank if not applicable.

| constraint | value |
| --- | --- |
| enum | `um`, `mm`, or `cm` |
| required | `False` |
| units for | `lc_length_value` |

<a name="lc_temp_value"></a>
##### [`lc_temp_value`](#lc_temp_value)
LC temperature. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `False` |

<a name="lc_temp_unit"></a>
##### [`lc_temp_unit`](#lc_temp_unit)
units for LC temperature. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| enum | `C` |
| required | `False` |
| units for | `lc_temp_value` |

<a name="lc_id_value"></a>
##### [`lc_id_value`](#lc_id_value)
LC column inner diameter (microns) Leave blank if not applicable.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `False` |

<a name="lc_id_unit"></a>
##### [`lc_id_unit`](#lc_id_unit)
units of LC column inner diameter (typically microns) Leave blank if not applicable.

| constraint | value |
| --- | --- |
| enum | `um`, `mm`, or `cm` |
| required | `False` |
| units for | `lc_id_value` |

<a name="lc_flow_rate_value"></a>
##### [`lc_flow_rate_value`](#lc_flow_rate_value)
Value of flow rate. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `False` |

<a name="lc_flow_rate_unit"></a>
##### [`lc_flow_rate_unit`](#lc_flow_rate_unit)
Units of flow rate. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |
| enum | `nL/min` or `mL/min` |
| units for | `lc_flow_rate_value` |

<a name="lc_gradient"></a>
##### [`lc_gradient`](#lc_gradient)
LC gradient. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |

<a name="lc_mobile_phase_a"></a>
##### [`lc_mobile_phase_a`](#lc_mobile_phase_a)
Composition of mobile phase A. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |

<a name="lc_mobile_phase_b"></a>
##### [`lc_mobile_phase_b`](#lc_mobile_phase_b)
Composition of mobile phase B. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |

<a name="processing_search"></a>
##### [`processing_search`](#processing_search)
Software for analyzing and searching LC-MS/MS omics data.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="processing_protocols_io_doi"></a>
##### [`processing_protocols_io_doi`](#processing_protocols_io_doi)
DOI for analysis protocols.io for this assay. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |
| pattern (regular expression) | `10\.17504/.*` |
| url | prefix: `https://dx.doi.org/` |

<a name="overall_protocols_io_doi"></a>
##### [`overall_protocols_io_doi`](#overall_protocols_io_doi)
DOI for protocols.io for the overall process for this assay. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |
| pattern (regular expression) | `10\.17504/.*` |
| url | prefix: `https://dx.doi.org/` |

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
| pattern (regular expression) | `[A-Z]+[0-9]+` |
| required | `True` |

<a name="tissue_id"></a>
##### [`tissue_id`](#tissue_id)
HuBMAP Display ID of the assayed tissue. Example: `ABC123-BL-1-2-3_456`.

| constraint | value |
| --- | --- |
| pattern (regular expression) | `([A-Z]+[0-9]+)-[A-Z]{2}\d*(-\d+)+(_\d+)?` |
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
| pattern (regular expression) | `10\.17504/.*` |
| url | prefix: `https://dx.doi.org/` |

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
| enum | `mass_spectrometry` |
| required | `True` |

<a name="assay_type"></a>
##### [`assay_type`](#assay_type)
The specific type of assay being executed.

| constraint | value |
| --- | --- |
| enum | `LC-MS (metabolomics)`, `LC-MS/MS (label-free proteomics)`, or `MS (shotgun lipidomics)` |
| required | `True` |

<a name="analyte_class"></a>
##### [`analyte_class`](#analyte_class)
Analytes are the target molecules being measured with the assay. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| enum | `protein`, `metabolites`, or `lipids` |
| required | `False` |

<a name="is_targeted"></a>
##### [`is_targeted`](#is_targeted)
Specifies whether or not a specific molecule(s) is/are targeted for detection/measurement by the assay.

| constraint | value |
| --- | --- |
| type | `boolean` |
| required | `True` |

### Unique to this type

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

<a name="ms_source"></a>
##### [`ms_source`](#ms_source)
The ion source type used for surface sampling (MALDI, MALDI-2, DESI, or SIMS) or LC-MS/MS data acquisition (nESI)

| constraint | value |
| --- | --- |
| required | `True` |

<a name="polarity"></a>
##### [`polarity`](#polarity)
The polarity of the mass analysis (positive or negative ion modes)

| constraint | value |
| --- | --- |
| enum | `negative ion mode` or `positive ion mode` |
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

<a name="data_collection_mode"></a>
##### [`data_collection_mode`](#data_collection_mode)
Mode of data collection in tandem MS assays. Either DDA (Data-dependent acquisition) or DIA (Data-independent acquisition).

| constraint | value |
| --- | --- |
| required | `True` |

<a name="ms_scan_mode"></a>
##### [`ms_scan_mode`](#ms_scan_mode)
Indicates whether experiment is MS, MS/MS, or other (possibly MS3 for TMT)

| constraint | value |
| --- | --- |
| required | `True` |

<a name="labeling"></a>
##### [`labeling`](#labeling)
Indicates whether samples were labeled prior to MS analysis (e.g., TMT)

| constraint | value |
| --- | --- |
| required | `True` |

<a name="section_prep_protocols_io_doi"></a>
##### [`section_prep_protocols_io_doi`](#section_prep_protocols_io_doi)
DOI for protocols.io referring to the protocol for preparing tissue sections for the assay.

| constraint | value |
| --- | --- |
| required | `True` |
| pattern (regular expression) | `10\.17504/.*` |
| url | prefix: `https://dx.doi.org/` |

<a name="lc_instrument_vendor"></a>
##### [`lc_instrument_vendor`](#lc_instrument_vendor)
The manufacturer of the instrument used for LC. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |

<a name="lc_instrument_model"></a>
##### [`lc_instrument_model`](#lc_instrument_model)
The model number/name of the instrument used for LC. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |

<a name="lc_column_vendor"></a>
##### [`lc_column_vendor`](#lc_column_vendor)
OPTIONAL: The manufacturer of the LC Column unless self-packed, pulled tip capilary is used. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |

<a name="lc_column_model"></a>
##### [`lc_column_model`](#lc_column_model)
The model number/name of the LC Column - IF custom self-packed, pulled tip calillary is used enter "Pulled tip capilary". Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |

<a name="lc_resin"></a>
##### [`lc_resin`](#lc_resin)
Details of the resin used for lc, including vendor, particle size, pore size. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |

<a name="lc_length_value"></a>
##### [`lc_length_value`](#lc_length_value)
LC column length. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `False` |

<a name="lc_length_unit"></a>
##### [`lc_length_unit`](#lc_length_unit)
units for LC column length (typically cm) Leave blank if not applicable.

| constraint | value |
| --- | --- |
| enum | `um`, `mm`, or `cm` |
| required | `False` |
| units for | `lc_length_value` |

<a name="lc_temp_value"></a>
##### [`lc_temp_value`](#lc_temp_value)
LC temperature. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `False` |

<a name="lc_temp_unit"></a>
##### [`lc_temp_unit`](#lc_temp_unit)
units for LC temperature. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| enum | `C` |
| required | `False` |
| units for | `lc_temp_value` |

<a name="lc_id_value"></a>
##### [`lc_id_value`](#lc_id_value)
LC column inner diameter (microns) Leave blank if not applicable.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `False` |

<a name="lc_id_unit"></a>
##### [`lc_id_unit`](#lc_id_unit)
units of LC column inner diameter (typically microns) Leave blank if not applicable.

| constraint | value |
| --- | --- |
| enum | `um`, `mm`, or `cm` |
| required | `False` |
| units for | `lc_id_value` |

<a name="lc_flow_rate_value"></a>
##### [`lc_flow_rate_value`](#lc_flow_rate_value)
Value of flow rate. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `False` |

<a name="lc_flow_rate_unit"></a>
##### [`lc_flow_rate_unit`](#lc_flow_rate_unit)
Units of flow rate. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |
| enum | `nL/min` or `mL/min` |
| units for | `lc_flow_rate_value` |

<a name="lc_gradient"></a>
##### [`lc_gradient`](#lc_gradient)
LC gradient. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |

<a name="lc_mobile_phase_a"></a>
##### [`lc_mobile_phase_a`](#lc_mobile_phase_a)
Composition of mobile phase A. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |

<a name="lc_mobile_phase_b"></a>
##### [`lc_mobile_phase_b`](#lc_mobile_phase_b)
Composition of mobile phase B. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |

<a name="processing_search"></a>
##### [`processing_search`](#processing_search)
Software for analyzing and searching LC-MS/MS omics data.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="processing_protocols_io_doi"></a>
##### [`processing_protocols_io_doi`](#processing_protocols_io_doi)
DOI for analysis protocols.io for this assay. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |
| pattern (regular expression) | `10\.17504/.*` |
| url | prefix: `https://dx.doi.org/` |

<a name="overall_protocols_io_doi"></a>
##### [`overall_protocols_io_doi`](#overall_protocols_io_doi)
DOI for protocols.io for the overall process for this assay. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |
| pattern (regular expression) | `10\.17504/.*` |
| url | prefix: `https://dx.doi.org/` |

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
