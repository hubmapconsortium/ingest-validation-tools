```
Metadata TSV Errors:
  dataset-examples/bad-tsv-formats/submission/codex-metadata.tsv (as codex):
    Internal:
    - A field value does not conform to a constraint. On row 2, column "donor_id",
      "not-uuid" fails because constraint "pattern" is "[A-Z]+[0-9]+"
    - A field value does not conform to a constraint. On row 2, column "tissue_id",
      "not-uuid" fails because constraint "pattern" is "([A-Z]+[0-9]+)-[A-Z]{2}\d*(-\d+)+(_\d+)?"
    - The value does not match the schema type and format for this field. On row 2,
      column "execution_datetime", "not-time" fails because type is "datetime/%Y-%m-%d
      %H:%M"
    - A field value does not conform to a constraint. On row 2, column "protocols_io_doi",
      "10\.17504/protocols.io.menc3de" fails because constraint "pattern" is "10\.17504/.*"
    - A field value does not conform to a constraint. On row 2, column "analyte_class",
      "analyte_class" fails because constraint "enum" is "['protein']"
    - The value does not match the schema type and format for this field. On row 2,
      column "is_targeted", "is_targeted" fails because type is "boolean/default"
    - A field value does not conform to a constraint. On row 2, column "acquisition_instrument_vendor",
      "acquisition_instrument_vendor" fails because constraint "enum" is "['Keyence',
      'Zeiss']"
    - A field value does not conform to a constraint. On row 2, column "acquisition_instrument_model",
      "acquisition_instrument_model" fails because constraint "enum" is "['BZ-X800',
      'BZ-X710', 'Axio Observer Z1']"
    - The value does not match the schema type and format for this field. On row 2,
      column "resolution_x_value", "forty-two" fails because type is "number/default"
    - A field value does not conform to a constraint. On row 2, column "resolution_x_unit",
      "inches" fails because constraint "enum" is "['mm', 'um', 'nm']"
    - The value does not match the schema type and format for this field. On row 2,
      column "resolution_y_value", "forty-two" fails because type is "number/default"
    - A field value does not conform to a constraint. On row 2, column "resolution_y_unit",
      "inches" fails because constraint "enum" is "['mm', 'um', 'nm']"
    - The value does not match the schema type and format for this field. On row 2,
      column "resolution_z_value", "forty-two" fails because type is "number/default"
    - A field value does not conform to a constraint. On row 2, column "resolution_z_unit",
      "inches" fails because constraint "enum" is "['mm', 'um', 'nm']"
    - A field value does not conform to a constraint. On row 2, column "preparation_instrument_vendor",
      "preparation_instrument_vendor" fails because constraint "enum" is "['CODEX']"
    - A field value does not conform to a constraint. On row 2, column "preparation_instrument_model",
      "preparation_instrument_model" fails because constraint "enum" is "['version
      1 robot', 'prototype robot - Stanford/Nolan Lab']"
    - The value does not match the schema type and format for this field. On row 2,
      column "number_of_antibodies", "0.5" fails because type is "integer/default"
    - The value does not match the schema type and format for this field. On row 2,
      column "number_of_channels", "0.5" fails because type is "integer/default"
    - The value does not match the schema type and format for this field. On row 2,
      column "number_of_cycles", "0.5" fails because type is "integer/default"
    - A field value does not conform to a constraint. On row 2, column "section_prep_protocols_io_doi",
      "not-doi" fails because constraint "pattern" is "10\.17504/.*"
    - A field value does not conform to a constraint. On row 2, column "reagent_prep_protocols_io_doi",
      "not-doi" fails because constraint "pattern" is "10\.17504/.*"
    External:
      row 2, referencing dataset-examples/bad-tsv-formats/submission/dataset-1:
        Not allowed:
        - channelnames.txt
        - cyc002_reg001_200216_112537/1_00001_Z001_CH1.tif
        - experiment.json
        - exposure_times.txt
        - segmentation.json
        Required but missing:
        - .+\.pdf
        - drv_[^/]+/channelNames\.txt
        - drv_[^/]+/processed_[^/]+/.*
        - src_[^/]+/channelnames\.txt
        - src_[^/]+/channelnames_report\.csv
        - src_[^/]+/cyc.*_reg.*_.*/.*_.*_Z.*_CH.*\.tif
        - src_[^/]+/experiment\.json
        - src_[^/]+/exposure_times\.txt
        - src_[^/]+/segmentation\.json
      row 2, contributors dataset-examples/bad-tsv-formats/submission/contributors.tsv: File
        has no data rows.
      row 2, antibodies dataset-examples/bad-tsv-formats/submission/antibodies.tsv: File
        does not exist
```
