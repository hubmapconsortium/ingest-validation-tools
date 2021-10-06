'''
>>> local_names = set(shared_enums['assay_type'])
>>> import requests
>>> canon_names = set(requests.get(
...    'https://search.api.hubmapconsortium.org/assaytype?simple=true&primary=true'
... ).json()['result'])

# >>> local_names - canon_names
# {}
'''

shared_enums = {
    'assay_category': [
        'imaging',
        'mass_spectrometry',
        'mass_spectrometry_imaging',
        'sequence'
    ],
    'assay_type': [
        '3D Imaging Mass Cytometry',
        'scRNA-Seq(10xGenomics)',
        'AF',
        'bulk RNA',
        'bulkATACseq',
        'Cell DIVE',
        'CE-MS',
        'CODEX',
        'DESI',
        'GC-MS',
        'Imaging Mass Cytometry',
        'LC-MS (metabolomics)',
        'LC-MS/MS (label-free proteomics)',
        'Light Sheet',
        'MxIF',
        'MALDI-IMS',
        'MS (shotgun lipidomics)',
        'NanoDESI',
        'NanoPOTS',
        'PAS microscopy',
        'scATACseq',
        'sciATACseq',
        'sciRNAseq',
        'seqFISH',
        'SIMS-IMS',
        'SNARE-seq2',
        'snATACseq',
        'snRNA',
        'SPLiT-Seq',
        'TMT (proteomics)',
        'WGS',
        'SNARE2-RNAseq',
        'snRNAseq',
        'scRNAseq-10xGenomics',  # Only needed for scrnaseq-v0.yaml.
        'scRNAseq-10xGenomics-v2',
        'scRNAseq-10xGenomics-v3',
        'scRNAseq',
        'Slide-seq',
        'MS Bottom-Up',
        'MS Top-Down',
        'LC-MS Top-Down',
        'LC-MS',
        'LC-MS Bottom-Up',
        'MS'
    ],
    'analyte_class': [
        'DNA',
        'RNA',
        'protein',
        'lipids',
        'metabolites',
        'polysaccharides',
        'metabolites_and_lipids',
        'glycans',
        'peptides',
        'phosphopeptides'
    ]
}
