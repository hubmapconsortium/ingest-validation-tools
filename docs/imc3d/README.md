# imc3d

Related files:
- [🔬 Background doc](https://portal.hubmapconsortium.org/docs/assays/imc): More details about this type.
- [📝 Excel template](https://raw.githubusercontent.com/hubmapconsortium/ingest-validation-tools/master/docs/imc3d/imc3d-metadata.xlsx): For metadata entry.
- [📝 TSV template](https://raw.githubusercontent.com/hubmapconsortium/ingest-validation-tools/master/docs/imc3d/imc3d-metadata.tsv): Alternative for metadata entry.
- [💻 Metadata schema](https://github.com/hubmapconsortium/ingest-validation-tools/edit/master/src/ingest_validation_tools/table-schemas/assays/imc3d.yaml): To update metadata fields.
- [💻 Directory schema](https://github.com/hubmapconsortium/ingest-validation-tools/edit/master/src/ingest_validation_tools/directory-schemas/imc3d.yaml): To update directory structure.

3D IMC submissions require metadata on the antibodies used in the assay to be provided in an Antibodies TSV. For 3D IMC, the `channel_id` is the name of the metal tag on the corresponding antibody.
The other fields function the same way for all assays using antibodies. For more information, see the [Antibodies TSV documentation](../antibodies).

## Directory schema

| pattern | required? | description |
| --- | --- | --- |
| `mcd/[^/]+_HuBMAP_[^/]+organ[^/]+_slide[^/]+\.zip` | ✓ | csv containing labels for sections as well as whether or not they were included in the 3D model |
| `mcd/section_report\.csv` | ✓ | **[QA/QC]** csv containing labels for sections as well as whether or not they were included in the 3D model |
| `mcd/channelnames_report\.csv` | ✓ | **[QA/QC]** CSV containing antibodies used and whether they were detected sufficiently or not |
| `3D_image_stack\.ome\.tiff` | ✓ | OME.tiff file comprising all slices and channels |
| `SingleCellData/cells\.csv` | ✓ | Contains one csv file per tissue with marker intensities (untransformed, range normalized to 99th percentile), phenograph cluster label and cell type label per single cell |
| `SingleCellData/cellsinfo\.txt` |  | Text file containing formatting information about cells*organ*.csv |
| `mapping/cluster_labels_image\.tif` | ✓ | Cell image labeled by cell type |
| `processed/umap_phenograph\.pdf` |  | tSNE phenograph |
| `processed/CellTypeComposition_perTissue\.pdf` |  | Cell type composition bar graph per tissue |
| `processed/Densityplots_perMarker\.pdf` |  | **[QA/QC]** Density plots of marker intensity, separated by marker |
| `processed/celltypes\.pdf` |  | Heatmap of marker expression per cluster, annotated by assigned cell type |
| `extras/.*` |  | Free-form descriptive information supplied by the TMC |
| `extras/thumbnail\.(png\|jpg)` |  | Optional thumbnail image which may be shown in search interface |

## Metadata schema


<details open="true"><summary><b>Version 1 (current)</b></summary>

<blockquote>

<details><summary>Shared by all types</summary>

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
<details><summary>Unique to this type</summary>

[`acquisition_instrument_vendor`](#acquisition_instrument_vendor)<br>
[`acquisition_instrument_model`](#acquisition_instrument_model)<br>
[`preparation_instrument_vendor`](#preparation_instrument_vendor)<br>
[`preparation_instrument_model`](#preparation_instrument_model)<br>
[`section_prep_protocols_io_doi`](#section_prep_protocols_io_doi)<br>
[`reagent_prep_protocols_io_doi`](#reagent_prep_protocols_io_doi)<br>
[`number_of_channels`](#number_of_channels)<br>
[`number_of_sections`](#number_of_sections)<br>
[`ablation_distance_between_shots_x_value`](#ablation_distance_between_shots_x_value)<br>
[`ablation_distance_between_shots_x_units`](#ablation_distance_between_shots_x_units)<br>
[`ablation_distance_between_shots_y_value`](#ablation_distance_between_shots_y_value)<br>
[`ablation_distance_between_shots_y_units`](#ablation_distance_between_shots_y_units)<br>
[`ablation_frequency_value`](#ablation_frequency_value)<br>
[`ablation_frequency_unit`](#ablation_frequency_unit)<br>
[`roi_description`](#roi_description)<br>
[`roi_id`](#roi_id)<br>
[`acquisition_id`](#acquisition_id)<br>
[`max_x_width_value`](#max_x_width_value)<br>
[`max_x_width_unit`](#max_x_width_unit)<br>
[`max_y_height_value`](#max_y_height_value)<br>
[`max_y_height_unit`](#max_y_height_unit)<br>
[`segment_data_format`](#segment_data_format)<br>
[`signal_type`](#signal_type)<br>
[`antibodies_path`](#antibodies_path)<br>
[`contributors_path`](#contributors_path)<br>
[`data_path`](#data_path)<br>
</details>

</blockquote>

### Shared by all types

##### `version`
Version of the schema to use when validating this metadata.
| constraint | value |
| --- | --- |
| enum | `1` |
| required | `True` |

##### `description`
Free-text description of this assay.
| constraint | value |
| --- | --- |
| required | `True` |

##### `donor_id`
HuBMAP Display ID of the donor of the assayed tissue. Example: `ABC123`.
| constraint | value |
| --- | --- |
| pattern (regular expression) | `[A-Z]+[0-9]+` |
| required | `True` |

##### `tissue_id`
HuBMAP Display ID of the assayed tissue. Example: `ABC123-BL-1-2-3_456`.
| constraint | value |
| --- | --- |
| pattern (regular expression) | `([A-Z]+[0-9]+)-[A-Z]{2}\d*(-\d+)+(_\d+)?` |
| required | `True` |

##### `execution_datetime`
Start date and time of assay, typically a date-time stamped folder generated by the acquisition instrument. YYYY-MM-DD hh:mm, where YYYY is the year, MM is the month with leading 0s, and DD is the day with leading 0s, hh is the hour with leading zeros, mm are the minutes with leading zeros.
| constraint | value |
| --- | --- |
| type | `datetime` |
| format | `%Y-%m-%d %H:%M` |
| required | `True` |

##### `protocols_io_doi`
DOI for protocols.io referring to the protocol for this assay.
| constraint | value |
| --- | --- |
| required | `True` |
| pattern (regular expression) | `10\.17504/.*` |
| url | prefix: `https://dx.doi.org/` |

##### `operator`
Name of the person responsible for executing the assay.
| constraint | value |
| --- | --- |
| required | `True` |

##### `operator_email`
Email address for the operator.
| constraint | value |
| --- | --- |
| format | `email` |
| required | `True` |

##### `pi`
Name of the principal investigator responsible for the data.
| constraint | value |
| --- | --- |
| required | `True` |

##### `pi_email`
Email address for the principal investigator.
| constraint | value |
| --- | --- |
| format | `email` |
| required | `True` |

##### `assay_category`
Each assay is placed into one of the following 3 general categories: generation of images of microscopic entities, identification & quantitation of molecules by mass spectrometry, and determination of nucleotide sequence.
| constraint | value |
| --- | --- |
| enum | `mass_spectrometry_imaging` |
| required | `True` |

##### `assay_type`
The specific type of assay being executed.
| constraint | value |
| --- | --- |
| enum | `3D Imaging Mass Cytometry` |
| required | `True` |

##### `analyte_class`
Analytes are the target molecules being measured with the assay.
| constraint | value |
| --- | --- |
| enum | `protein` |
| required | `True` |

##### `is_targeted`
Specifies whether or not a specific molecule(s) is/are targeted for detection/measurement by the assay. The CODEX analyte is protein.
| constraint | value |
| --- | --- |
| type | `boolean` |
| required | `True` |

### Unique to this type

##### `acquisition_instrument_vendor`
An acquisition instrument is the device that contains the signal detection hardware and signal processing software. Assays generate signals such as light of various intensities or color or signals representing the molecular mass.
| constraint | value |
| --- | --- |
| required | `True` |

##### `acquisition_instrument_model`
Manufacturers of an acquisition instrument may offer various versions (models) of that instrument with different features or sensitivities. Differences in features or sensitivities may be relevant to processing or interpretation of the data.
| constraint | value |
| --- | --- |
| required | `True` |

##### `preparation_instrument_vendor`
The manufacturer of the instrument used to prepare the sample for the assay.
| constraint | value |
| --- | --- |
| required | `True` |

##### `preparation_instrument_model`
The model number/name of the instrument used to prepare the sample for the assay.
| constraint | value |
| --- | --- |
| required | `True` |

##### `section_prep_protocols_io_doi`
DOI for protocols.io referring to the protocol for preparing tissue sections for the assay.
| constraint | value |
| --- | --- |
| required | `True` |
| pattern (regular expression) | `10\.17504/.*` |
| url | prefix: `https://dx.doi.org/` |

##### `reagent_prep_protocols_io_doi`
DOI for protocols.io referring to the protocol for preparing reagents for the assay.
| constraint | value |
| --- | --- |
| required | `True` |
| pattern (regular expression) | `10\.17504/.*` |
| url | prefix: `https://dx.doi.org/` |

##### `number_of_channels`
Number of mass channels measured.
| constraint | value |
| --- | --- |
| type | `integer` |
| required | `True` |

##### `number_of_sections`
Number of sections.
| constraint | value |
| --- | --- |
| type | `integer` |
| required | `True` |

##### `ablation_distance_between_shots_x_value`
x resolution. Distance between laser ablation shots in the X-dimension.
| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

##### `ablation_distance_between_shots_x_units`
Units of x resolution distance between laser ablation shots.
| constraint | value |
| --- | --- |
| enum | `um` or `nm` |
| required | `True` |

##### `ablation_distance_between_shots_y_value`
y resolution. Distance between laser ablation shots in the Y-dimension.
| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

##### `ablation_distance_between_shots_y_units`
Units of y resolution distance between laser ablation shots.
| constraint | value |
| --- | --- |
| enum | `um` or `nm` |
| required | `True` |

##### `ablation_frequency_value`
Frequency value of laser ablation (in Hz)
| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

##### `ablation_frequency_unit`
Frequency unit of laser ablation. Leave blank if not applicable.
| constraint | value |
| --- | --- |
| enum | `Hz` |
| required | `False` |
| units for | `ablation_frequency_value` |

##### `roi_description`
A description of the region of interest (ROI) captured in the image.
| constraint | value |
| --- | --- |
| required | `True` |

##### `roi_id`
Multiple images (1-n) are acquired from regions of interest (ROI1, ROI2, ROI3, etc) on a slide. The roi_id is a number from 1-n representing the ROI captured on a slide.
| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

##### `acquisition_id`
The acquisition_id refers to the directory containing the ROI images for a slide. Together, the acquisition_id and the roi_id indicate the slide-ROI represented in the image.
| constraint | value |
| --- | --- |
| required | `True` |

##### `max_x_width_value`
Image width value of the ROI acquisition.
| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

##### `max_x_width_unit`
Units of image width of the ROI acquisition. Leave blank if not applicable.
| constraint | value |
| --- | --- |
| enum | `um` |
| required | `False` |
| units for | `max_x_width_value` |

##### `max_y_height_value`
Image height value of the ROI acquisition.
| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

##### `max_y_height_unit`
Units of image height of the ROI acquisition. Leave blank if not applicable.
| constraint | value |
| --- | --- |
| enum | `um` |
| required | `False` |
| units for | `max_y_height_value` |

##### `segment_data_format`
This refers to the data type, which is a "float" for the IMC counts.
| constraint | value |
| --- | --- |
| enum | `float`, `integer`, or `string` |
| required | `True` |

##### `signal_type`
Type of signal measured per channel (usually dual counts)
| constraint | value |
| --- | --- |
| enum | `dual count`, `pulse count`, or `intensity value` |
| required | `True` |

##### `antibodies_path`
Relative path to file with antibody information for this dataset.
| constraint | value |
| --- | --- |
| required | `True` |

##### `contributors_path`
Relative path to file with ORCID IDs for contributors for this dataset.
| constraint | value |
| --- | --- |
| required | `True` |

##### `data_path`
Relative path to file or directory with instrument data. Downstream processing will depend on filename extension conventions.
| constraint | value |
| --- | --- |
| required | `True` |

</details>


<details ><summary><b>Version 0</b></summary>


### Shared by all types

##### `donor_id`
HuBMAP Display ID of the donor of the assayed tissue. Example: `ABC123`.
| constraint | value |
| --- | --- |
| pattern (regular expression) | `[A-Z]+[0-9]+` |
| required | `True` |

##### `tissue_id`
HuBMAP Display ID of the assayed tissue. Example: `ABC123-BL-1-2-3_456`.
| constraint | value |
| --- | --- |
| pattern (regular expression) | `([A-Z]+[0-9]+)-[A-Z]{2}\d*(-\d+)+(_\d+)?` |
| required | `True` |

##### `execution_datetime`
Start date and time of assay, typically a date-time stamped folder generated by the acquisition instrument. YYYY-MM-DD hh:mm, where YYYY is the year, MM is the month with leading 0s, and DD is the day with leading 0s, hh is the hour with leading zeros, mm are the minutes with leading zeros.
| constraint | value |
| --- | --- |
| type | `datetime` |
| format | `%Y-%m-%d %H:%M` |
| required | `True` |

##### `protocols_io_doi`
DOI for protocols.io referring to the protocol for this assay.
| constraint | value |
| --- | --- |
| required | `True` |
| pattern (regular expression) | `10\.17504/.*` |
| url | prefix: `https://dx.doi.org/` |

##### `operator`
Name of the person responsible for executing the assay.
| constraint | value |
| --- | --- |
| required | `True` |

##### `operator_email`
Email address for the operator.
| constraint | value |
| --- | --- |
| format | `email` |
| required | `True` |

##### `pi`
Name of the principal investigator responsible for the data.
| constraint | value |
| --- | --- |
| required | `True` |

##### `pi_email`
Email address for the principal investigator.
| constraint | value |
| --- | --- |
| format | `email` |
| required | `True` |

##### `assay_category`
Each assay is placed into one of the following 3 general categories: generation of images of microscopic entities, identification & quantitation of molecules by mass spectrometry, and determination of nucleotide sequence.
| constraint | value |
| --- | --- |
| enum | `mass_spectrometry_imaging` |
| required | `True` |

##### `assay_type`
The specific type of assay being executed.
| constraint | value |
| --- | --- |
| enum | `3D Imaging Mass Cytometry` |
| required | `True` |

##### `analyte_class`
Analytes are the target molecules being measured with the assay.
| constraint | value |
| --- | --- |
| enum | `protein` |
| required | `True` |

##### `is_targeted`
Specifies whether or not a specific molecule(s) is/are targeted for detection/measurement by the assay. The CODEX analyte is protein.
| constraint | value |
| --- | --- |
| type | `boolean` |
| required | `True` |

### Unique to this type

##### `acquisition_instrument_vendor`
An acquisition instrument is the device that contains the signal detection hardware and signal processing software. Assays generate signals such as light of various intensities or color or signals representing the molecular mass.
| constraint | value |
| --- | --- |
| required | `True` |

##### `acquisition_instrument_model`
Manufacturers of an acquisition instrument may offer various versions (models) of that instrument with different features or sensitivities. Differences in features or sensitivities may be relevant to processing or interpretation of the data.
| constraint | value |
| --- | --- |
| required | `True` |

##### `preparation_instrument_vendor`
The manufacturer of the instrument used to prepare the sample for the assay.
| constraint | value |
| --- | --- |
| required | `True` |

##### `preparation_instrument_model`
The model number/name of the instrument used to prepare the sample for the assay.
| constraint | value |
| --- | --- |
| required | `True` |

##### `section_prep_protocols_io_doi`
DOI for protocols.io referring to the protocol for preparing tissue sections for the assay.
| constraint | value |
| --- | --- |
| required | `True` |
| pattern (regular expression) | `10\.17504/.*` |
| url | prefix: `https://dx.doi.org/` |

##### `reagent_prep_protocols_io_doi`
DOI for protocols.io referring to the protocol for preparing reagents for the assay.
| constraint | value |
| --- | --- |
| required | `True` |
| pattern (regular expression) | `10\.17504/.*` |
| url | prefix: `https://dx.doi.org/` |

##### `number_of_channels`
Number of mass channels measured.
| constraint | value |
| --- | --- |
| type | `integer` |
| required | `True` |

##### `number_of_sections`
Number of sections.
| constraint | value |
| --- | --- |
| type | `integer` |
| required | `True` |

##### `ablation_distance_between_shots_x_value`
x resolution. Distance between laser ablation shots in the X-dimension.
| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

##### `ablation_distance_between_shots_x_units`
Units of x resolution distance between laser ablation shots.
| constraint | value |
| --- | --- |
| enum | `um` or `nm` |
| required | `True` |

##### `ablation_distance_between_shots_y_value`
y resolution. Distance between laser ablation shots in the Y-dimension.
| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

##### `ablation_distance_between_shots_y_units`
Units of y resolution distance between laser ablation shots.
| constraint | value |
| --- | --- |
| enum | `um` or `nm` |
| required | `True` |

##### `ablation_frequency_value`
Frequency value of laser ablation (in Hz)
| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

##### `ablation_frequency_unit`
Frequency unit of laser ablation. Leave blank if not applicable.
| constraint | value |
| --- | --- |
| enum | `Hz` |
| required | `False` |
| units for | `ablation_frequency_value` |

##### `roi_description`
A description of the region of interest (ROI) captured in the image.
| constraint | value |
| --- | --- |
| required | `True` |

##### `roi_id`
Multiple images (1-n) are acquired from regions of interest (ROI1, ROI2, ROI3, etc) on a slide. The roi_id is a number from 1-n representing the ROI captured on a slide.
| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

##### `acquisition_id`
The acquisition_id refers to the directory containing the ROI images for a slide. Together, the acquisition_id and the roi_id indicate the slide-ROI represented in the image.
| constraint | value |
| --- | --- |
| required | `True` |

##### `max_x_width_value`
Image width value of the ROI acquisition.
| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

##### `max_x_width_unit`
Units of image width of the ROI acquisition. Leave blank if not applicable.
| constraint | value |
| --- | --- |
| enum | `um` |
| required | `False` |
| units for | `max_x_width_value` |

##### `max_y_height_value`
Image height value of the ROI acquisition.
| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

##### `max_y_height_unit`
Units of image height of the ROI acquisition. Leave blank if not applicable.
| constraint | value |
| --- | --- |
| enum | `um` |
| required | `False` |
| units for | `max_y_height_value` |

##### `segment_data_format`
This refers to the data type, which is a "float" for the IMC counts.
| constraint | value |
| --- | --- |
| enum | `float`, `integer`, or `string` |
| required | `True` |

##### `signal_type`
Type of signal measured per channel (usually dual counts)
| constraint | value |
| --- | --- |
| enum | `dual count`, `pulse count`, or `intensity value` |
| required | `True` |

##### `antibodies_path`
Relative path to file with antibody information for this dataset.
| constraint | value |
| --- | --- |
| required | `True` |

##### `contributors_path`
Relative path to file with ORCID IDs for contributors for this dataset.
| constraint | value |
| --- | --- |
| required | `True` |

##### `data_path`
Relative path to file or directory with instrument data. Downstream processing will depend on filename extension conventions.
| constraint | value |
| --- | --- |
| required | `True` |

</details>
