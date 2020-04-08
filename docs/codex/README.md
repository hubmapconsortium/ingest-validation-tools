# codex

Related files:
- [JSON Schema](schema.yaml)
- [TSV Template](https://raw.githubusercontent.com/hubmapconsortium/ingest-validation-tools/master/docs/codex/template.tsv)

## Table of contents
[Provenance](#provenance)<br>
[`donor_id`](#donor_id)<br>
[`tissue_id`](#tissue_id)<br>
[Level 1](#level-1)<br>
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
[Level 2](#level-2)<br>
[`acquisition_instrument_vendor`](#acquisition_instrument_vendor)<br>
[`acquisition_instrument_model`](#acquisition_instrument_model)<br>
[`resolution_x_value`](#resolution_x_value)<br>
[`resolution_x_unit`](#resolution_x_unit)<br>
[`resolution_y_value`](#resolution_y_value)<br>
[`resolution_y_unit`](#resolution_y_unit)<br>
[`resolution_z_value`](#resolution_z_value)<br>
[`resolution_z_unit`](#resolution_z_unit)<br>
[Level 3](#level-3)<br>
[`preparation_instrument_vendor`](#preparation_instrument_vendor)<br>
[`preparation_instrument_model`](#preparation_instrument_model)<br>
[`number_of_antibodies`](#number_of_antibodies)<br>
[`number_of_channels`](#number_of_channels)<br>
[`number_of_cycles`](#number_of_cycles)<br>
[`section_prep_protocols_io_doi`](#section_prep_protocols_io_doi)<br>
[`reagent_prep_protocols_io_doi`](#reagent_prep_protocols_io_doi)<br>
[Paths](#paths)<br>
[`metadata_path`](#metadata_path)<br>
[`data_path`](#data_path)<br>

## Provenance

### `donor_id`
HuBMAP Display ID of the donor of the assayed tissue.

| constraint | value |
| --- | --- |
| required | `True` |
| pattern | `[A-Z]+[0-9]+` |

### `tissue_id`
HuBMAP Display ID of the assayed tissue.

| constraint | value |
| --- | --- |
| required | `True` |
| pattern | `[A-Z]+[0-9]+(-[A-Z0-9]+)+` |

## Level 1

### `execution_datetime`
Start date and time of assay. YYYY-MM-DD hh:mm +/-hh:mm, where YYYY is the year, MM is the month with leading 0s, and DD is the day with leading 0s, hh is the hour with leading zeros, mm are the minutes with leading zeros, followed by the offset from GMT.

| constraint | value |
| --- | --- |
| type | `datetime` |
| format | `%Y-%m-%d %H:%M %z` |
| required | `True` |

### `protocols_io_doi`
DOI for protocols.io referring to the protocol for this assay.

| constraint | value |
| --- | --- |
| required | `False` |
| pattern | `10\.17504/.*` |

### `operator`
Name of the person responsible for executing the assay.

| constraint | value |
| --- | --- |
| required | `True` |

### `operator_email`
Email address for the operator.

| constraint | value |
| --- | --- |
| format | `email` |
| required | `True` |

### `pi`
Name of the principal investigator responsible for the data.

| constraint | value |
| --- | --- |
| required | `True` |

### `pi_email`
Email address for the principal investigator.

| constraint | value |
| --- | --- |
| format | `email` |
| required | `True` |

### `assay_category`
Each assay is placed into one of the following 3 general categories: generation of images of microscopic entities, identification & quantitation of molecules by mass spectrometry, and determination of nucleotide sequence.

| constraint | value |
| --- | --- |
| required | `True` |
| enum | `['imaging', 'mass_spectrometry', 'sequence']` |

### `assay_type`
The specific type of assay being executed.

| constraint | value |
| --- | --- |
| required | `True` |
| enum | `['scRNA-Seq (10xGenomics)', 'AF', 'bulk RNA', 'bulkATACseq', 'CODEX', 'Imaging Mass Cytometry', 'LC-MS (metabolomics)', 'LC-MS/MS (label-free proteomics)', 'MxIF', 'IMS positive', 'IMS negative', 'MS (shotgun lipidomics)', 'PAS microscopy', 'scATACseq', 'sciATACseq', 'sciRNAseq', 'seqFISH', 'SNARE-seq2', 'snATACseq', 'snRNA', 'SPLiT-Seq', 'TMT (proteomics)', 'WGS']` |

### `analyte_class`
Analytes are the target molecules being measured with the assay.

| constraint | value |
| --- | --- |
| required | `True` |
| enum | `['DNA', 'RNA', 'protein', 'lipids', 'metabolites']` |

### `is_targeted`
Specifies whether or not a specific molecule(s) is/are targeted for detection/measurement by the assay .The CODEX analyte is protein.

| constraint | value |
| --- | --- |
| type | `boolean` |
| required | `True` |

## Level 2

### `acquisition_instrument_vendor`
An acquisition_instrument is the device that contains the signal detection hardware and signal processing software. Assays generate signals such as light of various intensities or color or signals representing molecular mass.

| constraint | value |
| --- | --- |
| required | `True` |

### `acquisition_instrument_model`
Manufacturers of an acquisition instrument may offer various versions (models) of that instrument with different features or sensitivities. Differences in features or sensitivities may be relevant to processing or interpretation of the data.

| constraint | value |
| --- | --- |
| required | `True` |

### `resolution_x_value`
The width of a pixel. (Akoya pixel is 377nm square)

| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

### `resolution_x_unit`
The unit of measurement of width of a pixel.(nm)

| constraint | value |
| --- | --- |
| required | `True` |
| enum | `['mm', 'um', 'nm']` |

### `resolution_y_value`
The height of a pixel. (Akoya pixel is 377nm square)

| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

### `resolution_y_unit`
The unit of measurement of height of a pixel. (nm)

| constraint | value |
| --- | --- |
| required | `True` |
| enum | `['mm', 'um', 'nm']` |

### `resolution_z_value`
Optional if assay does not have multiple z-levels. Note that this is resolution within a given sample: z-pitch (resolution_z_value) is the increment distance between image slices (for Akoya, z-pitch=1.5um) ie. the microscope stage is moved up or down in increments of 1.5um to capture images of several focal planes. The best one will be used & the rest discarded. The thickness of the sample itself is sample metadata.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `False` |

### `resolution_z_unit`
The unit of incremental distance between image slices.(um)

| constraint | value |
| --- | --- |
| required | `True` |
| enum | `['mm', 'um', 'nm']` |

## Level 3

### `preparation_instrument_vendor`
The manufacturer of the instrument used to prepare the sample for the assay.

| constraint | value |
| --- | --- |
| required | `True` |

### `preparation_instrument_model`
The model number/name of the instrument used to prepare the sample for the assay

| constraint | value |
| --- | --- |
| required | `True` |

### `number_of_antibodies`
Number of antibodies

| constraint | value |
| --- | --- |
| type | `integer` |
| required | `True` |

### `number_of_channels`
Number of fluorescent channels imaged during each cycle.

| constraint | value |
| --- | --- |
| type | `integer` |
| required | `True` |

### `number_of_cycles`
Number of cycles of 1. oligo application, 2. fluor application, 3. washes

| constraint | value |
| --- | --- |
| type | `integer` |
| required | `True` |

### `section_prep_protocols_io_doi`
DOI for protocols.io referring to the protocol for preparing tissue sections for the assay.

| constraint | value |
| --- | --- |
| required | `True` |
| pattern | `10\.17504/.*` |

### `reagent_prep_protocols_io_doi`
DOI for protocols.io referring to the protocol for preparing reagents for the assay.

| constraint | value |
| --- | --- |
| required | `True` |
| pattern | `10\.17504/.*` |

## Paths

### `metadata_path`
Relative path to file or directory with free-form or instrument/lab specific metadata. Optional.

| constraint | value |
| --- | --- |
| required | `False` |

### `data_path`
Relative path to file or directory with instrument data. Downstream processing will depend on filename extension conventions. Required.

| constraint | value |
| --- | --- |
| required | `True` |
