from typing import Dict, List


'''
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
'''
# The list above should be empty: There should be no mismatches;
# ie: All the assays listed below are recognized by the assay service.
#
# The assay_type list is *all* the values which have ever been used,
# including schemas which are currently deprecated.
# Each schema lists the particular values which are valid for it.
# This redundant list catches mistakes like a typo being introduced
# when an existing schema is versioned.

shared_enums: Dict[str, List[str]] = {
    'assay_type': [
        '3D Imaging Mass Cytometry',
        'AF',
        'Body CT',
        'CE-MS',
        'CODEX',
        'Cell DIVE',
        'DESI',
        'GC-MS',
        'Imaging Mass Cytometry',
        'LC-MS',
        'LC-MS(metabolomics)',
        'LC-MS Bottom-Up',
        'LC-MS Top-Down',
        'LC-MS/MS(label-free proteomics)',
        'Light Sheet',
        'MALDI-IMS',
        'MRI',
        'MS',
        'MS(shotgun lipidomics)',
        'MS Bottom-Up',
        'MS Top-Down',
        'Micro CT',
        'Multiplex Ion Beam Imaging',
        'MxIF',
        'NanoDESI',
        'NanoPOTS',
        'OCT',
        'PAS microscopy',
        'SIMS-IMS',
        'SNARE-seq2',
        'SNARE2-RNAseq',
        'Slide-seq',
        'Ultrasound',
        'WGS',
        'bulk RNA',
        'bulkATACseq',
        'scRNAseq',
        'scRNAseq-10xGenomics',
        'scRNAseq-10xGenomics-v2',
        'scRNAseq-10xGenomics-v3',
        'sciATACseq',
        'sciRNAseq',
        'seqFISH',
        'snATACseq',
        'snRNAseq',
        'snRNAseq-10xGenomics-v2',
        'snRNAseq-10xGenomics-v3',
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
    ],
    'assay_category': [
        'clinical_imaging',
        'imaging',
        'mass_spectrometry',
        'mass_spectrometry_imaging',
        'sequence'
    ],
}
