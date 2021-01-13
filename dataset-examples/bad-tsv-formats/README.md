```
Metadata TSV Errors:
  dataset-examples/bad-tsv-formats/submission/codex-metadata.tsv (as codex):
    Internal:
    - The value "not-uuid" in row 2 and column 1 ("A") does not conform to the pattern
      constraint of "[A-Z]+[0-9]+"
    - The value "not-uuid" in row 2 and column 2 ("B") does not conform to the pattern
      constraint of "([A-Z]+[0-9]+)-[A-Z]{2}\d*(-\d+)+(_\d+)?"
    - The value "not-time" in row 2 and column 3 ("C") is not type "datetime" and
      format "%Y-%m-%d %H:%M"
    - The value "10\.17504/protocols.io.menc3de" in row 2 and column 4 ("D") does
      not conform to the pattern constraint of "10\.17504/.*"
    - The value "operator_emailATexample.com" in row 2 and column 6 ("F") is not type
      "string" and format "email"
    - The value "pi_emailATexample.com" in row 2 and column 8 ("H") is not type "string"
      and format "email"
    - 'The value "analyte_class" in row 2 and column 11 ("K") does not conform to
      the given enumeration: "[''protein'']"'
    - The value "is_targeted" in row 2 and column 12 ("L") is not type "boolean" and
      format "default"
    - 'The value "acquisition_instrument_vendor" in row 2 and column 13 ("M") does
      not conform to the given enumeration: "[''Keyence'', ''Zeiss'']"'
    - 'The value "acquisition_instrument_model" in row 2 and column 14 ("N") does
      not conform to the given enumeration: "[''BZ-X800'', ''BZ-X710'', ''Axio Observer
      Z1'']"'
    - The value "forty-two" in row 2 and column 15 ("O") is not type "number" and
      format "default"
    - 'The value "inches" in row 2 and column 16 ("P") does not conform to the given
      enumeration: "[''mm'', ''um'', ''nm'']"'
    - The value "forty-two" in row 2 and column 17 ("Q") is not type "number" and
      format "default"
    - 'The value "inches" in row 2 and column 18 ("R") does not conform to the given
      enumeration: "[''mm'', ''um'', ''nm'']"'
    - The value "forty-two" in row 2 and column 19 ("S") is not type "number" and
      format "default"
    - 'The value "inches" in row 2 and column 20 ("T") does not conform to the given
      enumeration: "[''mm'', ''um'', ''nm'']"'
    - 'The value "preparation_instrument_vendor" in row 2 and column 21 ("U") does
      not conform to the given enumeration: "[''CODEX'']"'
    - 'The value "preparation_instrument_model" in row 2 and column 22 ("V") does
      not conform to the given enumeration: "[''version 1 robot'', ''prototype robot
      - Stanford/Nolan Lab'']"'
    - The value "0.5" in row 2 and column 23 ("W") is not type "integer" and format
      "default"
    - The value "0.5" in row 2 and column 24 ("X") is not type "integer" and format
      "default"
    - The value "0.5" in row 2 and column 25 ("Y") is not type "integer" and format
      "default"
    - The value "not-doi" in row 2 and column 26 ("Z") does not conform to the pattern
      constraint of "10\.17504/.*"
    - The value "not-doi" in row 2 and column 27 ("AA") does not conform to the pattern
      constraint of "10\.17504/.*"
    External:
      row 2, referencing dataset-examples/bad-tsv-formats/submission/dataset-1:
        Not allowed:
        - channelnames.txt
        - experiment.json
        - exposure_times.txt
        - segmentation.json
        Required but missing:
        - .+\.pdf
        - drv_[^/]+/channelNames\.txt
        - drv_[^/]+/experiment\.json
        - drv_[^/]+/exposure_times\.txt
        - drv_[^/]+/processed_[^/]+/.*
        - drv_[^/]+/segmentation\.json
        - src_[^/]+/channelnames\.txt
        - src_[^/]+/channelnames_report\.csv
      row 2, contributors dataset-examples/bad-tsv-formats/submission/contributors.tsv: File
        has no data rows.
      row 2, antibodies dataset-examples/bad-tsv-formats/submission/antibodies.tsv:
        Internal:
        - 'No such file or directory: ''dataset-examples/bad-tsv-formats/submission/antibodies.tsv'''
      row 2, protocols_io_doi 10\.17504/protocols.io.menc3de: 404
      row 2, section_prep_protocols_io_doi not-doi: 404
      row 2, reagent_prep_protocols_io_doi not-doi: 404
```
