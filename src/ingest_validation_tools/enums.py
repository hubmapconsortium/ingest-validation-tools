'''
>>> import requests
>>> local_names = shared_enums['assay_type']
>>> remote_mismatch = []
>>> for name in local_names:
...     response = requests.post(
...         'https://search.api.hubmapconsortium.org/assayname',
...         json={'name':name}, headers={'Content-Type': 'application/json'}).json()
...     if 'error' in response:
...         remote_mismatch.append(name)
>>> print('\\n'.join(remote_mismatch))
<BLANKLINE>
'''
# The list above should be empty: That means that all the assays
# listed below are recognized by the assay service.
# TODO: Joel will progressively uncomment names below, and when that is done
#       _validate_level_1_enum() can be renabled in schema_loader.py.

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
        # 'bulk RNA',
        'bulkATACseq',
        'Cell DIVE',
        # 'CE-MS',
        'CODEX',
        # 'DESI',
        # 'GC-MS',
        'Imaging Mass Cytometry',
        # 'LC-MS (metabolomics)',
        'LC-MS/MS (label-free proteomics)',
        'Light Sheet',
        'MxIF',
        'MALDI-IMS',
        # 'MS (shotgun lipidomics)',
        # 'NanoDESI',
        # 'NanoPOTS',
        'PAS microscopy',
        # 'scATACseq',
        'sciATACseq',
        'sciRNAseq',
        'seqFISH',
        # 'SIMS-IMS',
        'SNARE-seq2',
        'snATACseq',
        # 'snRNA',
        # 'SPLiT-Seq',
        # 'TMT (proteomics)',
        'WGS',
        'SNARE2-RNAseq',
        'snRNAseq',
        'scRNAseq-10xGenomics',  # Only needed for scrnaseq-v0.yaml.
        'scRNAseq-10xGenomics-v2',
        'scRNAseq-10xGenomics-v3',
        # 'scRNAseq',
        'Slide-seq',
        # 'MS Bottom-Up',
        # 'MS Top-Down',
        # 'LC-MS Top-Down',
        # 'LC-MS',
        # 'LC-MS Bottom-Up',
        # 'MS'
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
