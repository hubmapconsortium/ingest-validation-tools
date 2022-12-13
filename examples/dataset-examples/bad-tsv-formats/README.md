```
Metadata TSV Errors:
  examples/dataset-examples/bad-tsv-formats/upload/codex-metadata.tsv (as codex):
    Internal:
    - On row 2, column "donor_id", value "not-uuid" fails because constraint "pattern"
      is "[A-Z]+[0-9]+"
    - On row 2, column "tissue_id", value "not-uuid" fails because constraint "pattern"
      is "([A-Z]+[0-9]+)-[A-Z]{2}\d*(-\d+)+(_\d+)?"
    - On row 2, column "execution_datetime", value "not-time" fails because type is
      "datetime/%Y-%m-%d %H:%M"
    - On row 2, column "protocols_io_doi", value "10\.17504/protocols.io.menc3de"
      fails because constraint "pattern" is "10\.17504/.*"
    - On row 2, column "analyte_class", value "analyte_class" fails because constraint
      "enum" is "['protein']"
    - On row 2, column "is_targeted", value "is_targeted" fails because type is "boolean/default"
    - On row 2, column "acquisition_instrument_vendor", value "acquisition_instrument_vendor"
      fails because constraint "enum" is "['Keyence', 'Zeiss']"
    - On row 2, column "acquisition_instrument_model", value "acquisition_instrument_model"
      fails because constraint "enum" is "['BZ-X800', 'BZ-X710', 'Axio Observer Z1']"
    - On row 2, column "resolution_x_value", value "forty-two" fails because type
      is "number/default"
    - On row 2, column "resolution_x_unit", value "inches" fails because constraint
      "enum" is "['mm', 'um', 'nm']"
    - On row 2, column "resolution_y_value", value "forty-two" fails because type
      is "number/default"
    - On row 2, column "resolution_y_unit", value "inches" fails because constraint
      "enum" is "['mm', 'um', 'nm']"
    - On row 2, column "resolution_z_value", value "forty-two" fails because type
      is "number/default"
    - On row 2, column "resolution_z_unit", value "inches" fails because constraint
      "enum" is "['mm', 'um', 'nm']"
    - On row 2, column "preparation_instrument_vendor", value "preparation_instrument_vendor"
      fails because constraint "enum" is "['CODEX']"
    - On row 2, column "preparation_instrument_model", value "preparation_instrument_model"
      fails because constraint "enum" is "['version 1 robot', 'prototype robot - Stanford/Nolan
      Lab']"
    - On row 2, column "number_of_antibodies", value "0.5" fails because type is "integer/default"
    - On row 2, column "number_of_channels", value "0.5" fails because type is "integer/default"
    - On row 2, column "number_of_cycles", value "0.5" fails because type is "integer/default"
    - On row 2, column "section_prep_protocols_io_doi", value "not-doi" fails because
      constraint "pattern" is "10\.17504/.*"
    - On row 2, column "reagent_prep_protocols_io_doi", value "not-doi" fails because
      constraint "pattern" is "10\.17504/.*"
    External:
      row 2, data examples/dataset-examples/bad-tsv-formats/upload/dataset-1:
        Not allowed:
        - channelnames.txt
        - cyc002_reg001_200216_112537/1_00001_Z001_CH1.tif
        - experiment.json
        - exposure_times.txt
        - segmentation.json
        Required but missing:
        - (processed|drv_[^/]*)/.*
        - (raw|processed)/config\.txt|(src_[^/]*|drv_[^/]*)/[sS]egmentation\.json
        - (raw|src_.*)/.*
        - (raw|src_.*)/[cC]yc.*_reg.*/.*_Z.*_CH.*\.tif
        - (raw|src_[^/]*)/[Ee]xperiment\.json
      row 2, contributors examples/dataset-examples/bad-tsv-formats/upload/contributors.tsv: File
        has no data rows.
      row 2, antibodies examples/dataset-examples/bad-tsv-formats/upload/antibodies.tsv: File
        does not exist
Reference Errors:
  No References:
    Files:
    - dataset-1
Hint: 'If validation fails because of extra whitespace in the TSV, try:

  src/cleanup_whitespace.py --tsv_in original.tsv --tsv_out clean.tsv'
```
