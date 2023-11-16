from typing import Dict, List


"""
>>> import requests
>>> local_names = shared_enums['assay_type']
>>> remote_mismatch = []
>>> for name in local_names:
...     response = requests.post(
...         'https://search.api.hubmapconsortium.org/assayname',
...         json={'name': name},
...         headers={'Content-Type': 'application/json'}
...     ).json()
...     if 'error' in response:
...         remote_mismatch.append(name)
>>> print(remote_mismatch)
[]
"""
# The list above should be empty: There should be no mismatches;
# ie: All the assays listed below are recognized by the assay service.
#
# The assay_type list is *all* the values which have ever been used,
# including schemas which are currently deprecated.
# Each schema lists the particular values which are valid for it.
# This redundant list catches mistakes like a typo being introduced
# when an existing schema is copied, pasted, and tweaked to make a new version.

shared_enums: Dict[str, List[str]] = {
    "assay_type": [
        "10x Multiome",
        "3D Imaging Mass Cytometry",
        "AF",
        "ATACseq",
        "ATACseq (bulk)",
        "Auto-fluorescence",
        "bulk-RNA",
        "bulkATACseq",
        "Cell DIVE",
        "Cell Dive",
        "cell-dive",
        "CE-MS",
        "CODEX",
        "CODEX2",  # TODO: Temporary; will be removed.
        # https://github.com/hubmapconsortium/ingest-validation-tools/issues/1107
        "Confocal",
        "CosMx",
        "CyCIF",
        "DESI",
        "Enhanced Stimulated Raman Spectroscopy (SRS)",
        "GC-MS",
        "GeoMx",
        "GeoMx (RNA)",
        "GeoMx (protein)",
        "HiFi-Slides",
        "Histology",
        "DBiT",
        "2D Imaging Mass Cytometry",
        "Imaging Mass Cytometry",
        "IMS",
        "LC-MS (metabolomics)",
        "LC-MS/MS (label-free proteomics)",
        "Light Sheet",
        "MxIF",
        "MALDI",
        "MALDI-IMS",
        "MERFISH",
        "MS (shotgun lipidomics)",
        "MIBI",
        "Multiplex Ion Beam Imaging",
        "Molecular Cartography",
        "NanoDESI",
        "NanoPOTS",
        "nanoSPLITS",
        "PAS microscopy",
        "PhenoCycler",
        "Publication",
        "publication",
        "RNAseq",
        "RNAseq (bulk)",
        "RNAseq (GeoMx)",
        "RNAseq (Visium)",
        "sciATACseq",
        "sciRNAseq",
        "seqFISH",
        "Second Harmonic Generation",
        "SIMS",
        "SIMS-IMS",
        "SNARE-seq2",
        "snATACseq",
        "scATAC-seq",
        "WGS",
        "SNARE2-RNAseq",
        "snRNAseq",  # equivalent to snRNAseq-10xGenomics-v3
        "scRNAseq-10xGenomics",  # Only needed for scrnaseq-v0.yaml.
        "scRNAseq-10xGenomics-v2",
        "scRNAseq-10xGenomics-v3",
        "snRNAseq-10xGenomics-v2",
        "snRNAseq-10xGenomics-v3",
        "scRNAseq",
        "scRNA-seq",
        "Slide-seq",
        "MS Bottom-Up",
        "MS Top-Down",
        "LC-MS Top-Down",
        "LC-MS",
        "LC-MS Bottom-Up",
        "MS",
        "Body CT",
        "Micro CT",
        "OCT",
        "MRI",
        "Ultrasound",
        "Thick Section Multiphoton MxIF",
        "Visium",
        "Xenium",
    ],
    "analyte_class": [
        "DNA",
        "RNA",
        "protein",
        "lipids",
        "metabolites",
        "polysaccharides",
        "metabolites_and_lipids",
        "glycans",
        "peptides",
        "phosphopeptides",
    ],
    "assay_category": [
        "clinical_imaging",
        "fish",
        "imaging",
        "histology",
        "mass_spectrometry",
        "mass_spectrometry_imaging",
        "mxfbe",
        "organ",
        "sample",
        "sequence",
        "single_cycle_fluorescence_microscopy",
        "spatial_transcriptomics",
    ],
}
