from enum import Enum, unique
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
        "GeoMx (nCounter)",
        "GeoMx (NGS)",
        "HiFi-Slide",
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
        "MUSIC",
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
        "RNAseq (with probes)",
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
        "Visium (with probes)",
        "Visium (no probes)",
        "Xenium",
        "Segmentation Mask",
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
        "derived_datasets",
    ],
}


@unique
class EntityTypes(str, Enum):

    # TODO: I believe this can be streamlined with the StrEnum class added in 3.11
    @classmethod
    def value_list(cls) -> List[str]:
        return [entity_type.value for entity_type in cls]

    @classmethod
    def key_list(cls) -> List[str]:
        return [entity_type.name.lower() for entity_type in cls]

    @classmethod
    def get_enum_from_val(cls, val) -> str:
        match = [entity_type for entity_type in cls if entity_type.value == val]
        if not match:
            return ""
        return match[0]


class DatasetType(EntityTypes):
    DATASET = "dataset"


class OtherTypes(EntityTypes):
    ANTIBODIES = "antibodies"
    CONTRIBUTORS = "contributors"
    SOURCE = "source"
    SAMPLE = "sample"
    ORGAN = "organ"
    DONOR = "donor"

    @classmethod
    def get_sample_types(cls):
        return Sample.key_list()

    @classmethod
    def get_sample_types_full_names(cls):
        return Sample.value_list()

    @classmethod
    def with_sample_subtypes(cls, with_sample=True):
        all_types = [entity_type for entity_type in [*cls, *Sample]]
        if not with_sample:
            all_types.remove(OtherTypes.SAMPLE)
        return all_types


class Sample(EntityTypes):
    BLOCK = "sample-block"
    SUSPENSION = "sample-suspension"
    SECTION = "sample-section"
    ORGAN = "organ"

    @classmethod
    def with_parent_type(cls):
        return [*[entity_type for entity_type in cls], OtherTypes.SAMPLE]
