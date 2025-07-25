# Changelog

## v0.0.37 (in progress)
- Update Xenium directory schema
- Update Publication directory schema
- Update Xenium directory schema
- Update Validator param to refer to SchemaVersion rather than TSV
- Add Stereo-seq directory schema
- Check dataset ancestors to prevent registration against organs of type Other
- Update geomx metadata docs
- Update GeoMx directory schema
- Update GeoMx dir schema
- Update GeoMx directory schema
- Update Auto-fluorescence directory schema
- Update Visium directory schema
- Update Visium no probes directory schema
- Update GeoMx NGS directory schema
- Update MERFISH directory schema
- Add FACS passthrough dataset type
- Update FACS directory schema
- Add support for CosMx Transcriptomics/Proteomics
- Update CosMx Transcriptomics directory schema
- Update CosMx Proteomics directory schema
- Update FACS directory schema
- Add CyCIF dataset
- Create docs for FACS
- Add Olink passthrough dataset type
- Update MERFISH directory schema
- Add proteomics docs category
- Fixed test for changelog
- Update MERFISH directory schema
- Add Seq-Scope passthrough data type, directory schema

## v0.0.36
- Update Xenium directory schema
- Update LC-MS directory schema
- Bugfix table_schema logic for legacy validation
- Remove CyCIF

## v0.0.35
 - Adding support for EPIC's new plugin
 - Update MERFISH directory schema
 - Update Histology directory schema
 - Update 2D Imaging Mass Cytometry directory schema
 - Update DESI directory schema
 - Update MALDI directory schema
 - Update Multiplex Ion Beam Imaging directory schema
 - Update SIMS directory schema
 - Update CODEX directory schema
 - Update Cell DIVE directory schema
 - Update Phenocycler directory schema
 - Update Auto-fluorescence directory schema
 - Update Confocal directory schema
 - Update Enhanced Stimulated Raman Spectroscopy directory schema
 - Update Light Sheet directory schema
 - Update Second Harmonic Generation directory schema
 - Update Thick Section Multiphoton MxIF directory schema
 - Update CosMX directory schema
 - Update GeoMx NGS directory schema
 - Update Visium no probes directory schema
 - Update Visium with probes directory schema
 - Update Xenium directory schema
 - Update Segmentation Mask directory schema
 - Create DBiT-seq directory schema
 - Add G4X directory schema
 - Update docs for g4x & dbit-seq

## v0.0.34
 - Create CyTOF directory schema
 - Update MERFISH directory schema
 - Update Histology directory schema
 - Update 2D Imaging Mass Cytometry directory schema
 - Update DESI directory schema
 - Update MALDI directory schema
 - Update Multiplex Ion Beam Imaging directory schema
 - Update SIMS directory schema
 - Update CODEX directory schema
 - Update Cell DIVE directory schema
 - Update Phenocycler directory schema
 - Update Auto-fluorescence directory schema
 - Update Confocal directory schema
 - Update Enhanced Stimulated Raman Spectroscopy directory schema
 - Update Light Sheet directory schema
 - Update Second Harmonic Generation directory schema
 - Update Thick Section Multiphoton MxIF directory schema
 - Update CosMX directory schema
 - Update GeoMx NGS directory schema
 - Update Visium no probes directory schema
 - Update Visium with probes directory schema
 - Update Xenium directory schema
 - Update Segmentation Mask directory schema
 - Undo version 2.3 updates and keep version 2.4 updates to CosMx directory schema

## v0.0.33
- Update Xenium directory schema
- Update Xenium directory schema
- Update CosMx directory schema

## v0.0.32
- Update Xenium directory schema
- Adding new is_schema_latest_version method to check if provided Cedar spec is the latest
- Fix issue with json response. On row {x}, column {fieldName} should NOT be concatenated with actual error message.

## v0.0.31
- Update Segmentation masks directory schema
- Update Cell DIVE directory schema
- Bugfix shared upload non_global file error reporting

## v0.0.30
- Update Seg Mask documentation
- Update CosMx directory schema
- Constrain file patterns to end of line for all published directory schemas
- Handle null responses for keys from assayclassifier endpoint
- Remove assumption of table_schema and version corresponding to table_schema from SchemaVersion
- Update fixture data with new UBKG responses

## v0.0.29
- Add CosMX directory schema
- Update CosMX directory schema
- Update Segmentation masks directory schema
- Update Auto-fluorescence directory schema
- Update CODEX directory schema
- Update CODEX directory schema

## v0.0.28
- Update Xenium directory schema
- Update GeoMx NGS directory schema
- Add CosMX metadata schema

## v0.0.27
- Update Visium with probes directory schema pt 3
- Update Segmentation masks directory schema
- Updating tests based on new dir schema major versions and assayclassifier responses
- Removing references to deprecated Search API endpoint 'assayname'
- Update Phenocycler directory schema
- Update GeoMx NGS directory schema
- Update shared upload check
- Release Xenium
- Create Xenium directory schema
- Error reporting changes, addition of summarized counts
- Update Segmentation Mask link

## v0.0.26
- Update GeoMx NGS directory schema
- Update MERFISH directory schema
- Update LC-MS directory schema
- Update Visium with probes directory schema
- Update Visium with probes directory schema pt 2

## v0.0.25
- Update GeoMx NGS directory schema
- Added EPIC dataset field derived_dataset_type to UNIQUE_FIELDS_MAP

## v0.0.24
- Release MERFISH
- Add MERFISH directory schema
- Fix documentation issue for MERFISH
- Add CEDAR link for MERFISH
- Update MERFISH directory schema
- Update Phenocycler docs
- Update MERFISH directory schema
- Add next-gen Cell DIVE directory schema
- Update MIBI directory schema
- Update Visium no probes directory schema
- Add Cell DIVE to index
- Update Segmentation Masks directory schema
- Update Visium with probes directory schema
- Update Visium no probes directory schema
- Update Visium with probes directory schema
- Update Visium no probes directory schema
- Change to EntityTypeInfo constraint format to support constraints endpoint

## v0.0.23
- Add token to validation_utils.get_assaytype_data, replace URL string concatenation with urllib

## v0.0.22
- Fix logging length issue in Upload.multi_parent
- Minor change to Visium with probes directory schema
- Minor change to Visium no probes directory schema
- Update docs for Visium directories

## v0.0.21
- Fix the changelog to reflect the current version.
- Fix row number mismatch between validation and spreadsheet validator response

## v0.0.20
- Fix row number mismatch between validation and spreadsheet validator response

## v0.0.19
- Directory validation changes for "shared" uploads
- Update Phenocycler directory schema
- Remove bad paths from LC-MS directory schema
- Allow multiple comma-separated parent_sample_id values
- Accommodate dir schema minor versions
- Fix ORCID URL checking
- Add MUSIC next-gen directory schema
- Updating documentation
- Change Upload error output to dataclass
- Revert deprecation of field YAML files
- Update MUSIC directory schema
- Add semantic version to plugin test base class
- Fix row number mismatch between validation and spreadsheet validator response
- Adding entity constraints check
- Adding ability to report names of successfully run plugins

## v0.0.18

- Update PhenoCycler directory schema
- Update to prevent standalone child datasets in multi-assay upload
- Update to prevent multiple dataset types in a non-multi-assay upload
- Update MIBI directory schema
- Update Visium (with probes) directory schema
- Update Auto-fluorescence directory schema
- Update Confocal directory schema
- Update Enhanced SRS directory schema
- Update Light Sheet directory schema
- Update Second Harmonic Generation directory schema
- Update Thick Section Multiphoton MxIF directory schema
- Integrate SenNet app_context
- Updating testing
- Change to error messaging related to get_assaytype_data failures
- Update Lightsheet directory schema
- Update Histology to include description on OME-TIFFs
- Update Histology with links
- Update GeoMx NGS directory schema
- Ported murine from SenNet
- Update Histology directory schema
- Bugfix stripping trailing slash in ingest api url
- Converted upload `_url_checks` to use `_get_method` for SenNet compatibility
- Add CEDAR template for murine-source
- Add donor field descriptions back, remove murine-source descriptions
- Temporarily exclude certain assays from the documentation

## v0.0.17

- Update atacseq cedar link
- Add Phenocycler next-gen directory schema
- Update Histology next-gen directory schema
- Add LC-MS next-gen directory schema
- Add GeoMx NGS next-gen directory schema
- Update PhenoCycler and Histology to 2.2.0
- Update CEDAR links for PhenoCycler & Histology
- Refactor Upload to avoid validating the same contributors.tsv multiple times / running plugins over files multiple times
- Add entry for segmentation-mask
- Modify directory schema validation such that it takes empty directories into account
- Add Publication next-gen directory schema
- Update ATAC/RNA/10X documentation
- Update Cell Dive documentation
- Update to support passing list of data_paths to ingest-validation-tests plugins
- Adding linting/formatting GitHub actions

## v0.0.16

- add support for Publication type
- updated issue templates.
- removed donor metadata spec (had not been in use)
- Added examples for fields with pattern constraint
- Replaced `preparation_temperature` with `preparation_condition` and updated associated enumerations in the sample-section, sample-block, and sample-suspension schemas
- Replaced `storage_temperature` with `storage_method` and updated associated enumerations in the sample-section, sample-block, and sample-suspension schemas
- Updated enum 'bulk RNA' assay type to be 'bulk-RNA' across tools
- Adding organ v2 schema
- Added publication docs
- Removed double publication enum (P/p)
- Updated publication directory schema 20230616
- Changes for CEDAR docs
- Tweaks for CEDAR release
- Release new assays with links
- Fix in place to avoid assay conflicts with new assays
- Rework wording for CEDAR updates
- Updated upload.py to integrate CEDAR validation, replaced walrus operators, removed unused import
- Updated CEDAR validation routine based on changes to Spreadsheet Validator
- Updated tests based on changes to error dict structure
- Tested both CEDAR and local validation paths
- Make changes to Histology based on feedback
- Update documentation based on feedback
- Addtional changes to Histology
- Adding SenNet display changes
- Add contributor TSV CEDAR checking
- Add CEDAR examples
- Update CEDAR links for set of assays
- Split docs into current and deprecated
- Update Visium CEDAR template link
- Remove Visium draft attribute
- Bugfix datetime constraint in library_creation_date.yaml
- Update LCMS and add NanoSplits
- Update descriptions for segmentation masks
- Add description to codex doc page
- Bail earlier in validation if there are errors in metadata/dir/refs
- Update Antibodies
- Remove NanoSplits
- Update hifi, mibi, imc
- Fix imc-2d docs
- Fix imc-2d dir docs
- Add link to OME-Tiff docs
- Remove WGS, CE-MS, GC-MS, and RNAseq (GeoMx)
- Update histology and segmentation mask directory schemas
- Update hifi-slide to hifi-slides
- Fix changelog error
- Fix CI
- Update MIBI and IMC2D directory schemas
- Fix to support display of errors for CEDAR template metadata
- Upate Auto-fluorescence, Confocal, and Light Sheet directory schemas
- Additional updates to next-gen histology directory schema
- Implemented soft assay types/assayclassifier endpoint for canonical assay names and dir structures
- Added mock response test data for offline testing
- Add more assays
- Correct Auto-fluorescence lab_processed/annotations path description
- Add Visium with probes next-gen directory schema
- Update MALDI, SIMS, DESI, Visium no probes, and HiFi-Slide directory schemas
- Fix paths in Histology, MIBI, IMC2D, AF, Confocal, Light Sheet, and Visium with probes directory schemas
- Add CODEX, Thick section Multiphoton MxIF, Second Harmonic Generation, and Enhanced Stimulated Raman Spectroscopy (SRS) next-gen directory schemas
- Move Thick section Multiphoton MxIF next-gen directory schema to placeholder file
- Update file path in Visium no probes, Histology, AF, MxIF, SHG, SRS, Confocal, Light Sheet, MALDI, SIMS, DESI
- Remove Organ CEDAR page
- Draft next-gen directory schema for SNARE-seq2
- Added multi-assay support
- Delete GeoMX
- Update soft typing to use hyphen, not underscore
- Add SNARE-seq2 and RNAseq with probes next-gen directory schema
- Remove the draft tag from SNARE-seq2
- Regenerate docs for SNARE-seq2

## v0.0.15 - 2023-04-04

- Versioned directory structure schema
- Added MxIF directory structure schema.
- Added Lightsheet version 1.
- bump nokogiri -> 1.13.9 (dependabot)
- Add front-matter to exclude HCA from toc
- Updated CODEX version 0 and documentation.
- Provide an iterator over plugin test classes
- Updated CODEX version 0.
- Added Bulk RNA-seq directory structure schema.
- Added SeqFISH directory structure schema.
- Add a reminder that TSV validation is not sufficient.
- Clearer presentation of unit fields in generated docs.
- Make `contributors_path` required for HCA.
- Parallelize tests.
- Use the assay service to describe how assays are represented in the Portal.
- Adding Comma Separated File support for tissue_id.
- Update assay type for Cell DIVE.
- Updated suspension-fields.yaml and associated files in /docs/sample-suspension.
- Created extra_parameter on upload for future dynamic adding.
- Updated ErrorReport class to be backwards compatible with external calls.
- Added geoMX directory structure schema.
- Update `preparation_maldi_matrix` in imaging MS schema to from enum to open string field.
- Expand file types for stained to not be vendor locked to Leica's `.scn`. Include vendor-neutral `.tiff`.
- Replaced enum `Multiplexed Ion Beam Imaging` with `MIBI` in src
- Added `raw` as a potential directory to look for `segmentation.json` file for `CODEX`.
- Updated error messages to be less programmer centric.
- Updated ims-v2 spec to include DESI as an acceptable enumeration for ms_source.
- Upgraded CI python definition to 3.9.
- Update Cell DIVE with CEDAR UUID
- Add Histology directory schemas
- Fix Histology schema
- Modify validation routine to support multi-assay schemas
- Update MALDI, SIMS, and CODEX
- Update DESI and remove NanoDESI
- Support for conditional directory validation

## v0.0.14 - 2022-06-23

- bump tzingo -> 1.2.10 (dependabot)
- Turn validation of enums back on.
- Mods to plugin validator to fix import problems.
- Return directory schema version and refactor.
- Add new data_collection_mode values for MS assays.
- Add "CODEX2" assay type.
- Deprecate older LCMS schemas.
- Updated LC-MS directory structure schema.
- Remove HTML reporting options.
- Updated IMS directory structure schema.
- Add Clinical Imaging schemas.
- Test under both Python 3.6 and Python 3.10
- Cosmetic updates to the Slide-seq directory structure schema.
- Fix rendering bug on CODEX page by adding linebreaks.
- Add type hints.
- Implement versioning for directory schemas.
- After failure, explain how to continue testing from last error.
- Add `pathology_distance_unit` in place.
- Pin transitive dependencies.
- New sample metadata schemas
- Darker shade of blue, to be consistent with portal.
- Dependabot upgrade to Nokogiri.
- Remove reference to old Travis envvar, so post-merge CI run will pass.
- Explain the distinction between the 10X kit versions.
- Updated CODEX directory structure schema.
- Added MIBI directory structure schema.
- add snRNAseq-10xGenomics-v3
- Make backward incompatible changes to ims-v2 in place, without a new version.
- Preserve the key order in generated YAML, for readability.
- Add 'Multiplex Ion Beam Imaging' assay name
- Permanently remove snRNA and scATACseq assay names
- add snRNAseq-10xGenomics-v2 to the scrnaseq assays
- Move "Unique to this type" below the acquisition instrument fields.
- Add CLI option to allow the use of deprecated schemas.
- Allowing trailing slashes on dataset directories in metadata TSV.
- Add acquisition instrument fields to MIBI that were left out by mistake.
- Just use pytest to run doctests
- Headers are no longer properties of fields.
- Remove mention of `extras/thumbnail.jpg`.
- Add release date to schema.
- Add UMI fields to scrnaseq schema.
- Add Excel sheet describing which fields show up in which schemas.
- Add field descriptions to spreadsheet.
- Temporarily disable checking the assay names in schemas against the global list.
  Entries in the global list are now commented out, and Joel will progressively
  uncomment them.
- Moved `dataset.json` to `raw` or `src_*` directory for CODEX datasets.
- Modify IMC docs

## v0.0.13 - 2022-01-07

- Make more fields explicitly numeric
- Add more donor field descriptions.
- Deprecate contributors-v0.
- Add MIBI schema.
- Add fields for LCMS v3.
- Consistent rendering of code blocks in github pages and github preview.
- Warn about trailing slashes in paths.
- Optionally, dump validation report at the top of the upload.
- In the report notes, record the version of the checkout.
- Improve testing of `generate_field_yaml.py`.
- Provides map in docs/ from fields to the entities and assays they are used in.
- Give schema and version in success message.
- Generate `field-types.yaml`.
- Update assay list.
- Added WGS directory structure schema.
- Fixed regex on directory structure schema.
- Check that assay terms match approved list. (Right now, they don't.)
- Level 1 description of assay_category: Updated "3" assay categories to "4". Added imaging mass spec.
- work around mypy importlib type hinting problem
- Cleaned up LC-MS directory structure schema.
- Added links to examples in the portal for 5 assays.
- Make LC fields optional.
- Present directory path examples in same column.
- Updated LC-MS directory structure schema.
- Work around mypy importlib type hinting problem.
- Longer assay description for LCMS, and supporting machinery.
- In CI, pin to older Ubuntu version to avoid SSL problems with Uniprot.
- Level 1 description of assay_category: Updated "3" assay categories to "4".
- Added imaging mass spec.
- Work around mypy importlib type hinting problem.
- Antibodies validation is broken; Move test out the way.
- Make email validation effective.
- Add a test to confirm that backslashes aren't ignored during validation.
- Explain allowed values for booleans.
- Update the lcms schema field "lc_temp_value" optional
- Switch to Github CI.
- `cell_barcode_read` description: comma-delimitted.
- Update the lcms schema field "lc_temp_value" optional.
- Hit a different URL for ORCID, that will not give us soft 404s.
- In bash scripts, make python3 explicit.
- Update the flowchart to reflect the roles of Bill and PK.
- Add pipeline info.
- Hotfix on CellDive directory to reflect changes to dataset.
- Updated CellDive directory structure.
- Updated CODEX directory structure.
- Non-assay schema docs were not be update. Fix that.
- Sample was being skipped in doc generation. Fix that.
- Add to enums for `perfusion_solutions` and `ms_source`.
- Upgrade from dependabot.

## v0.0.12 - 2021-07-23

- Catch unrecognized keys in dir schema.
- Ammend LCMS docs.
- Fix CI: point to right branch.
- Document Donor and Sample Metadata process.
- Make the network cache file JSON, for portability.
- Dependabot update.
- Fix typo.
- Explain acronyms.
- Add kwarg to pass-through to tests.
- Update `validate_upload.py` docs.
- Add new LCMS version, and clean up reused fields.
- Make barcode fields optional.
- User donor as a test-bed for ontology-enums.
- Add a warning on pages where every version has been deprecated.
- Add gcms.
- Make some scatacseq fields optional.
- Create CE-MS.
- New version of IMS.
- Add a warning on pages where every version has been deprecated.
- Doc test for deprecated schemas.
- Add 10X multiome to scatacseq.
- Deprecated flag can now be added to schema.
- CLEANUP rnaseq_assay_method.
- cleanup resolution_z_unit.
- Network problems in report, instead of quitting with stack trace.
- New lightsheet schema, with description of changes.
- Introduced Lightsheet directory schema.
- Ensure that version numbers match the constraint inside the file.
- `maldiims` to `ims`: Only touches URLs; doesn't affect validation.
- Add script to validate any TSV.
- Factor out exit status codes.
- Pull out sc_isolation_tissue_dissociation.
- sequencing_read_format is optional for HCA.
- Disallow N/A values.
- Pull out the fields that have only one variant.
- Cleanup code for reference validations.
- Better section headers.
- Tighter validation of shared fields in assay schemas.
- Another optional field in HCA scrnaseq.
- Cleanup whitespace in yaml.
- Tools to resolve duplicated field definitions.
- Rearrange YAML so static processing works.

## v0.0.11 - 2021-05-18

- Updated AF and stained microscopy structure schema.
- Updated CODEX directory structure schema.
- No Donor and Tissue ID validation needed for HCA.
- Longer description for Q30.
- Setup GH Pages.
- Fix bug with loading non-HCA schemas that have an HCA variant.
- Fix bug in the `maldiims` schema to use correct file name extension
- Update description of the `.ibd` and `.imzML` files in the `maldiims` schema
- Added example `maldiims` folder structure
- Updated README.md to reflect the `examples/...` folder structure
- Use assay names to make titles.
- Add formalin as a Sample perfusion_solution.
- Style the GH Pages like the portal.
- Catch metadata TSVs with non-ASCII characters.
- More general ignore forurl-status-cache.
- Support Windows environments by converting back-slashes for forward slashes.
- Improve navigation and styling of new GH Pages.
- In cleanup_whitespace.py, avoid printing extra newlines on windows.
- Field templates for sequencing fields.
- Missing `data_path` will no longer cause spurious errors when submission is interpretted as dataset.
- README for `examples/` directory.
- Distinct error codes for different situations.
- Field templates for library fields.
- More doctests.
- Loosen sequential items check, and improve error message.
- Replace "submission" with "upload".

## v0.0.10 - 2021-04-21

- Remove inappropriate syntax highlighting from CLI docs.
- Fix bug in report generation.
- Remove contributors_path from HCA.
- Make the codeowners more granular.
- Distinguish v2 and v3 10x.
- Add expected_cell_count.
- Remove the sequence_limit where not appropriate.
- Chuck missed `source_project` in scrnaseq-hca: Added now.
- Distinguish v2 and v3 10x, and add to HCA as well.
- Add 'Belzer MPS/KPS' as an option.
- Remove links to YAML from MD.
- Cleaned up description on 3D IMC directory schema.
- Updated a description on 3D IMC directory schema.
- Updated regular expression on CODEX directory schema.
- Fix the generated TOC for antibodies.
- Apply "units_for": Units only required is value is given.
- Check for auto-incremented fields.
- If it errors, add a note about cleanup_whitespace.py.
- Apply missing constraints to scrnaseq.
- Consistent pattern constraint for sequencing_read_format.
- Diagram of overall repo structure; Explain doc build process.
- Remove vestigial "Level 3".
- Fixed typo in CODEX directory schema.
- Make more fields optional in HCA scrnaseq.
- Make it work with Python 3.6.
- Create subdirectories for `examples` and `tests` to clean up the top level.
- Add v1 for all schemas.
- Introduce scrnaseq-hca.
- Look for a `source_project` field to distinguish schemas.
- Move script docs into subdirectory, and improve coverage.
- Put TOC in blockquote: semantics are't right, but it indents.
- Simplify sample ID regex.
- Cache network responses to disk.
- Add the generated YAML to the output directory.
- Generate a report about the metadata values used in Elasticsearch.

## v0.0.9 - 2021-03-16

- Fix typo in CellDIVE.
- Update CLI usage to highlight sample validation.
- Update lightsheet docs.
- Update IMC docs.
- Add concentration to antibodies.
- Factor out Frictionless to give us more control over table validation.
- Check for CSV instead of TSV.
- Better error message for missing and mis-ordered fields.
- No longer require contributor middle names.
- Make network checks a part of the schema; Skip None values.
- Check for values which Excel has "helpfully" auto-incremented.
- Add 4C as a preservation temperature.
- Add units_for, so unused units aren't needed in the spreadsheet.
- Ivan is primary contact for directory work.
- Make network checks a part of the schema.
- Get rid of special-purpose logic for level-1
- Fix typo in nano enum.
- Clearer error when it can't find matching assay name.
- Downgrade dependency for compatibility with HuBMAP commons.
- Directory structure for scatacseq.
- Add 3D IMC table and directory schemas.
- Link to the yaml for both directory and metadata schemas.
- Directory structure for scatacseq and scrnaseq: They share a symlink.
- Add help document.
- Factor out the checks, make OO, and make error messages configurable.
- Slightly better errors when a directory is found when a TSV is expected.
- Make as_text_list the default output format.
- Script to generate CSV for fields and enums.
- Add version number to schemas.
- Clarify guidelines for direction schemas.

## v0.0.8 - 2021-02-10

- Update CODEX directory structure
- Allow "X" as final character of ORCID.
- Ping the respective services to confirm the ORCIDs, RR IDs, and Uniprot IDs are actually good.
- Add encoding as CLI param.
- Add `--offline` option, and use it internally.
- Fix the CLI parameter parsing: Either `--local_directory` or `--tsv_paths` must be provided.
- Allow examples of path rexes to be provided, and fix bug.
- Use the SciCrunch resolver for RR IDs.
- More helpful message if decoding error.
- State stability policy.
- Show the URL that produced the 404, and unify the code.
- Warning if missing "assay_type".
- Add lightsheet.
- Add a slot for a free-text note.
- Friendlier error if trying to validate Antibodies or Contributors as metadata.
- Update directory description docs.
- Upgrade to latest version of Frictionless. The content of error messages has changed.
- Clarify description of CODEX channelnames_report.csv.
- Add flowchart documenting the consensus submission process.
- cleanup-whitespace.py
- Issue templates to operationalize new process for handling post-release changes.
- Support versioning of metadata schemas.
- Add channel_id description to CellDIVE

## v0.0.7 - 2021-01-13

- Improved error messages in Excel.
- Define donor terms.
- Update MALDI terms.
- Demonstrate that validation of one-line-tsv-in-directory will work.
- Add an include mechanism to reduce duplication in the configs, and use it.
- Add Celldive.
- Add an include mechanism to reduce duplication in the configs.
- New organs will be coming in. Loosen regex.
- Give test.sh an optional argument, to pick-up the test run in the middle.
- Remove wildcards from dir schemas which have not been delivered.
- Update Celldive and CODEX directory schemas.
- Sort file errors for stability.
- Check protocols io DOIs.
- Remove option to validate against directory structure in Globus.
- Loosen ID regex to allow lymph nodes. (Chuck's mistake!)

## v0.0.6 - 2020-12-07

- Add thumbnail to directory schema.
- Add machinery to include regex examples in docs.
- Run mypy, but only on the one file that has type annotations.
- Consolidate TSV reading to avoid inconsistencies in character encoding.
- Remove option for directory schema "subtypes".
- Read type from first line of TSV, instead of from filename.
- Remove vestigial line from flake8 config.
- Instructions for working groups providing descriptions.
- Remove extraneous parts from Sample doc.
- Document contributors.tsv
- Warn if two TSVs are for the same assay type.
- Give example of single TSV validation.
- Add SLIDEseq.
- Add antibodies.tsv.
- Generate Excel files.
- Fix a commandline hint when tests fail.
- Escape RE in directory schema.
- Unify generation of assay and other docs.
- Supply XLSX for non-assays.
- Fix links.
- Unconstrain channel_id and uniprot.
- SLIDEseq dir schema.
- Test validation of antibodies.tsv

## v0.0.5 - 2020-11-09

- Change "mixif" to "mxif".
- Expose sample field descriptions for use in portal.
- Add missing assay type to enum.
- ng/ul to nM.
- Change to flat directory schema structure.
- Dir Schema for MALDI-IMS.
- AF dir schema.
- Update README, and diagram.
- Add extras directory.
- Prettier HTML output.
- Add donor.yaml, where we can explain donor metadata fields, and hook it into field-descriptions.yaml.
- Add ingest-validation-tests submodule.
- nanodesi/pots table schema.
- Add as_text_list option.
- plugin_validator started.
- Add donor.yaml, where we can explain donor metadata fields.
- Fix the build.
- Now that we have agreed on extras/, expose in docs.
- Contributors table schema.
- Add extra validation hooks.
- Add nano docs.
- Run plugin tests only from command line argument
- Add stained imagery directory schema.
- Update CODEX directory schema: Require PDF.
- Get rid of unified.yaml.
- Point at docs on portal.
- Remove missing example.
- Add is_qa_qc to dir schema table.
- Add passing contributors.tsv

## v0.0.4 - 2020-06-26

### Added

- Add Sample field descriptions.
- Change to "validate_samples".
- Get enums in sync, and doctest the logic.
- Add liquid nitrogen
- Revise sample metadata.
- Fix Regexes in MD.
- Sample metadata validation
- ... and fill in draft details.
- ... and fill in headers and add unit columns.
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
- New note to clarify git is required.
