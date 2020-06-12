# Changelog

## v0.0.4 - In progress
### Added
- Sample metadata validation: Fill in draft details.
- Fill in TODOs.
- Generate unified description list.
- Links to background docs.
- Pre-fill enums in TSVs
- Generator will stub the Level-1 overrides.
- Units on IMC.
- Submission structure diagram.
- Autogenerate "Leave blank if not applicable".
- Add bulkrnaseq and bulkatacseq.
- Add WGS and IMC.
- Dump unified yaml for each type. (This will be pulled on the portal side.)
- Add enum constraints to unit fields, and replace TODOs.
- Check that directory schemas exist.
### Changed
- Simplified directory validation.
- mass -> mz.
- bulkrnaseq QA is just RIN.
- Add bytes to IMC.
- LCMS capitals.
- Update wgs enum
- More accurate sample ID regex.
- Reorder LCMS fields.
- `atacseq` to `scatacseq`.
- Make sc_isolation_enrichment in scrnaseq optional.
- Free-form cell_barcode_read.
- Add bulkrnaseq, bulkatacseq, and wgs fields.
- mass/charge is unitless in MS: Remove field.
- TSV parsing conforms to excel-tsv: No longer ignoring backslashes.
- More explicit label for patterns in MD.
- TSV filenames match what will be required downstream.
- IMS -> MALDI-IMS
### Removed
- avg_insert_size from bulkatacseq.

## [v0.0.3](https://github.com/hubmapconsortium/ingest-validation-tools/tree/v0.0.3) - 2020-05-04
### Added
- Additional scrnaseq types and columns.
- Add a number of Assay types for Vanderbilt.
- Friendlier error if data_path is missing.
- Add polysaccharides as analyte_class.
- Ignore glob patterns and not just fixed files.
If other patterns are given, dot-files must be explicitly ignored.
### Changed
- Remove parenthesis from assay type.
- Assume Latin-1 encoding for TSVs rather than UTF-8.
- Update LC-MS fields.
- Separate level-2 schemas in source.
- Separate type and TSV path with space instead of ":" in CLI.
- Make analyte_class optional for some assays.
- Tweak LCMS fields.

## [v0.0.2](https://github.com/hubmapconsortium/ingest-validation-tools/tree/v0.0.2) - 2020-04-25
### Added
- Mirror Globus directory to local cache.
- Fix `--type_metadata` so it still works without a submission directory.
- Add `--optional_fields` to temporarily ignore the given fields.
- Add `--ignore_files` to ignore particular top-level files.
- Ignore dot-files. No command-line option to enable stricter validation, for now.
- Add scrnaseq.
- Open error report in browser.
### Changed
- Make the ATACseq validation more flexible.
- Less confusing representation of enums in docs.
- Allow lower level schemas to override aspects of the Level 1 schema.
- Make DOIs required again: Fields to consider optional can be set on commandline.
- Add more options to atacseq enum.
- Update CODEX directory schema to match what is actually delivered.

## [v0.0.1](https://github.com/hubmapconsortium/ingest-validation-tools/tree/v0.0.1) - 2020-04-13
### Added
- Validate structure of Akoya CODEX submissions.
- Generate submission template.
- Check that fixture-based tests actually ran.
- Check types early, rather than waiting for file-not-found.
- Generate JSON Schema from simpler Table Schema.
- Use schema to check that submission headers are correct, and reference by letter if not.
- Filling in details for CODEX Schema.
- Stanford directory schema.
- Convert column numbers to spreadsheet-style letters.
- Table of contents in generated doc.
- Added number_of_channels
- Added constraints to generated docs.
- Support timezone offset (rather than abbreviation).
- Add ATAC-seq and revise schema; fixed caps; Added descriptions.
- Validate DOIs for protocols.io.
- Added "Paths" section to both.
- Make periods in blank lines optional.
- Make fields required.
- Validate donor and sample IDs.
- Check that CLI docs are up to date.
- Validate the data_path.
- Allow multiple metadata.tsvs.
- Validate against Globus.
- Support multiple TSVs.
- Use <details> in ToC.
- Link to Google doc spec.
- Allow Globus File Browser URL to be used directly.
- Gratuitous Emojis!
- seqfish
- Deeply structured YAML error reports.
- Check for multiply referenced, or unreferenced paths.
### Changed
- CSV -> TSV
- Make the schema validation errors more readable
- Doctests are scanned from directory, rather than read from single file.
- Change the modeling of replicate groups.
- `parent_id` to `tissue_id`
- Link to raw TSV.
- No more UUIDs.
- Ignore blank lines in TSV.
- Tighter numeric constraints on ATAC-seq.
- Generate all docs at once.
- Add more enums.
- Unify Level 1 metadata definitions.
- Revert DOI format.
- No longer checking consistency of donor and sample.
- Remove generic schema.
- python3 in hash-bang.
- Reorganize fixtures.
- Stop generating JSON Schema, for now.
- Define path fields only in one place.
- Remove timezone offset.
- Autogenerate parts of table schema.
