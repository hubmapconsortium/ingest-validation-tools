```
Directory Errors:
  examples/dataset-examples/bad-tsv-formats/upload/dataset-1 (as codex-v1.1):
  - Not allowed:
    - channelnames.txt.
    - cyc002_reg001_200216_112537/1_00001_Z001_CH1.tif.
    - experiment.json.
    - exposure_times.txt.
    - segmentation.json.
    Required but missing:
    - (processed|drv_[^/]*)/.*.
    - (raw|src_.*)/.*.
    - (raw|src_.*)/[cC]yc.*_reg.*/.*_Z.*_CH.*\.tif.
    - (raw|src_[^/]*)/dataset\.json.
    - extras/dir-schema-v1-with-dataset-json.
Antibodies/Contributors Errors:
  examples/dataset-examples/bad-tsv-formats/upload/codex-metadata.tsv:
  - 'Error opening or reading value "contributors.tsv" from column "contributors_path":
    File has no data rows: examples/dataset-examples/bad-tsv-formats/upload/contributors.tsv.'
  - 'Value "antibodies.tsv" in column "antibodies_path" points to non-existent file:
    "examples/dataset-examples/bad-tsv-formats/upload/antibodies.tsv".'
Local Validation Errors:
  examples/dataset-examples/bad-tsv-formats/upload/codex-metadata.tsv (as codex-v0):
  - 'On row 2, column "donor_id", value "not-uuid" fails because it does not match
    the expected pattern. Example: ABC123'
  - 'On row 2, column "tissue_id", value "not-uuid" fails because it does not match
    the expected pattern. Example: ABC123-BL-1-2-3_456'
  - On row 2, column "execution_datetime", value "not-time" fails because it is not
    in the format YYYY-MM-DD Hour:Minute.
  - On row 2, column "protocols_io_doi", value "10\.17504/protocols.io.menc3de" fails
    because it does not match the expected pattern.
  - 'On row 2, column "analyte_class", value "analyte_class" fails because it is not
    one of these: "protein".'
  - On row 2, column "is_targeted", value "is_targeted" fails because it is neither
    true nor false.
  - 'On row 2, column "acquisition_instrument_vendor", value "acquisition_instrument_vendor"
    fails because it is not one of these: "Keyence", "Zeiss".'
  - 'On row 2, column "acquisition_instrument_model", value "acquisition_instrument_model"
    fails because it is not one of these: "BZ-X800", "BZ-X710", "Axio Observer Z1".'
  - On row 2, column "resolution_x_value", value "forty-two" fails because it is not
    in numerical form.
  - 'On row 2, column "resolution_x_unit", value "inches" fails because it is not
    one of these: "mm", "um", "nm".'
  - On row 2, column "resolution_y_value", value "forty-two" fails because it is not
    in numerical form.
  - 'On row 2, column "resolution_y_unit", value "inches" fails because it is not
    one of these: "mm", "um", "nm".'
  - On row 2, column "resolution_z_value", value "forty-two" fails because it is not
    in numerical form.
  - 'On row 2, column "resolution_z_unit", value "inches" fails because it is not
    one of these: "mm", "um", "nm".'
  - 'On row 2, column "preparation_instrument_vendor", value "preparation_instrument_vendor"
    fails because it is not one of these: "CODEX".'
  - 'On row 2, column "preparation_instrument_model", value "preparation_instrument_model"
    fails because it is not one of these: "version 1 robot", "prototype robot - Stanford/Nolan
    Lab".'
  - On row 2, column "number_of_antibodies", value "0.5" fails because it is not an
    integer.
  - On row 2, column "number_of_channels", value "0.5" fails because it is not an
    integer.
  - On row 2, column "number_of_cycles", value "0.5" fails because it is not an integer.
  - On row 2, column "section_prep_protocols_io_doi", value "not-doi" fails because
    it does not match the expected pattern.
  - On row 2, column "reagent_prep_protocols_io_doi", value "not-doi" fails because
    it does not match the expected pattern.
  - On row 2, column "protocols_io_doi", value "10\.17504/protocols.io.menc3de" fails
    because it is an invalid DOI.
  - On row 2, column "section_prep_protocols_io_doi", value "not-doi" fails because
    it is an invalid DOI.
  - On row 2, column "reagent_prep_protocols_io_doi", value "not-doi" fails because
    it is an invalid DOI.
Fatal Errors: 'Skipping plugins validation: errors in upload metadata or dir structure.'
```