---
title: Segmentation Mask
schema_name: segmentation-mask
category: Derived Datasets
all_versions_deprecated: False
exclude_from_index: False
layout: default

---

Related files:

Excel and TSV templates for this schema will be available when the draft next-generation schema, to be used in all future submissions, is finalized (no later than Sept. 30).

For additional documentation on Segmentation Masks, please visit [here](https://docs.google.com/document/d/1TSQon8nTIoyA5bEKxd8IAKYO6nsDabGbbQ8uKN1gj4E).

## Metadata schema


<summary><a href="https://docs.google.com/spreadsheets/d/1sMMyKtrxD_PO4TVj0JhOpeLF0fRYe2Fjmxnhp-fNzdM"><b>Version 2 (use this one)</b> (draft - submission of data prepared using this schema will be supported by Sept. 30)</a></summary>



<br>

## Directory schemas
<summary><b>Version 2.0 (use this one)</b></summary>

| pattern | required? | description |
| --- | --- | --- |
| <code>derived\/.*</code> | ✓ | The EPIC data is placed in TOP/derived/ so it does not conflict with any files if it is uploaded with a primary dataset. |
| <code>derived\/extras\/.*</code> | ✓ | Folder for general lab-specific files related to the derived dataset. |
| <code>derived\/segmentation_masks\/.*</code> | ✓ | Directory containing segmentation masks. |
| <code>derived\/segmentation_masks\/[^\/]+\.segmentations.ome.tiff</code> | ✓ | The segmentation masks should be stored as multi-channel pyramidal OME TIFF bitmasks with one channel per mask, where a single mask contains all instances of a type of object (e.g., all cells, a class of FTUs, etc). The class of objects contained in the mask is documented in the segmentation-masks.csv file. Each individual object in a mask should be represented by a unique integer pixel value starting at 1, with 0 meaning background (e.g., all pixels belonging to the first instance of a T-cell have a value of 1, the pixels for the second instance of a T-cell have a value of 2, etc). The pixel values should be unique within a mask. FTUs and other structural elements should be captured the same way as cells with segmentation masks and the appropriate channel feature definitions. |
| <code>derived\/segmentation_masks\/[^\/]+-objects\.(?:tsv&#124;xlsx)</code> | ✓ | This is a matrix where each row describes an individual object (e.g., one row per cell in the case where a mask contains all cells) and columns are features (i.e., object type, marker intensity, classification strategies, etc). One file should be created per mask with the name of the mask prepended to the file name. For example, if there is a cell segmentation map called "cells" then you would include a file called "cells-objects.csv" and that file would contain one row per cell in the "cells" mask and one column per feature, such as marker intensity and/or cell type. A minimum set of fields (required and optional) is included below. |
| <code>derived\/segmentation_masks\/[^\/]+-centroid-adjacency\.csv</code> |  | Objects are required to be in the same mask. A separate centroid-adjacency file can be included per mask. |
| <code>derived\/segmentation_masks\/[^\/]+-linkage-adjacency\.csv</code> |  | Objects are required to be in the same mask. A separate linkage-adjacency file can be included per mask. |
| <code>derived\/segmentation_masks\/[^\/]+-mesh\.glb</code> |  | This is a file with 3D mesh images for a 3D map. |
| <code>derived\/segmentation_masks\/transformations\/.*</code> |  | This directory should include any transformation files that pertain to a 3D reconstruction from serial sections. The mask protocol should explain the structure of these transformation files and how they can be used to reconstruct the 3D map from the 2D sections. |

