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
- Add ATAC-seq; fixed caps; Added descriptions.
- Validate DOIs for protocols.io.
- Added "Paths" section to both.
### Changed
- CSV -> TSV
- Make the schema validation errors more readable
- Doctests are scanned from directory, rather than read from single file.
- Change the modeling of replicate groups.
- `parent_id` to `tissue_id`
- Link to raw TSV.
