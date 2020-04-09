# Changelog

## v0.0.1 - In progress
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
- Support multiple TSVs
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
