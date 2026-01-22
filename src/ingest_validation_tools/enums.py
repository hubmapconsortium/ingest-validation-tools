from enum import Enum, unique


@unique
class EntityTypes(str, Enum):

    @classmethod
    def value_list(cls) -> list[str]:
        return [entity_type.value for entity_type in cls]

    @classmethod
    def key_list(cls) -> list[str]:
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


# These should all be considered to be mutually exclusive,
# even within the same type
UNIQUE_FIELDS_MAP = {
    OtherTypes.ANTIBODIES: {"antibody_rrid", "antibody_name"},
    OtherTypes.CONTRIBUTORS: {"orcid", "orcid_id"},
    DatasetType.DATASET: {"assay_type", "dataset_type", "derived_dataset_type"},
    OtherTypes.SOURCE: {"strain_rrid"},
    OtherTypes.ORGAN: {"organ_id"},  # Deprecated
    OtherTypes.SAMPLE: {"sample_id"},
}
OTHER_FIELDS_UNIQUE_FIELDS_MAP = {
    k: v for k, v in UNIQUE_FIELDS_MAP.items() if not k == DatasetType.DATASET
}


class CedarSchemaVersionTypes(str, Enum):
    IS_LATEST_VERSION = "isLatestVersion"
    IS_LATEST_PUBLISHED_VERSION = "isLatestPublishedVersion"
    IS_LATEST_DRAFT_VERSION = "isLatestDraftVersion"


class ReportType(Enum):
    STR = 1
    JSON = 2


# DEPRECATED, preserved for legacy functionality only
shared_enums: dict[str, list[str]] = {
    "assay_type": [
        "4i",
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
        "CODEX2",
        "Confocal",
        "CosMx Transcriptomics",
        "CosMx Proteomics",
        "DESI",
        "Enhanced Stimulated Raman Spectroscopy (SRS)",
        "FACS",
        "GC-MS",
        "GeoMx",
        "GeoMx (RNA)",
        "GeoMx (protein)",
        "GeoMx (nCounter)",
        "GeoMx (NGS)",
        "HiFi-Slide",
        "Histology",
        "DBiT-seq",
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
        "Olink",
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
        "Seq-Scope",
        "Second Harmonic Generation",
        "SIMS",
        "SIMS-IMS",
        "Singular Genomics G4X",
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
        "Stereo-seq",
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
        "CyTOF",
        "CyCIF",
        "Object x Analyte",
        "Visium HD",
        "Pixel-seqV2",
        "MPLEx",
        "STARmap",
        "Raman Imaging",
        "iCLAP",
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
        "proteomics",
        "sample",
        "sequence",
        "single_cycle_fluorescence_microscopy",
        "spatial_transcriptomics",
        "derived_datasets",
        "flow_cytometry",
    ],
}
