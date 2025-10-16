---
title: Segmentation Mask
schema_name: segmentation-mask
category: Derived Datasets
all_versions_deprecated: False
exclude_from_index: False
layout: default

---
Prepare your metadata based on the latest metadata schema using one of the template files below. See the instructions in the [Metadata Validation Workflow](https://docs.google.com/document/d/1lfgiDGbyO4K4Hz1FMsJjmJd9RdwjShtJqFYNwKpbcZY) document for more information on preparing and validating your metadata.tsv file prior to submission.

Related files:


- [📝 Excel template](https://raw.githubusercontent.com/hubmapconsortium/dataset-metadata-spreadsheet/main/segmentation-mask/latest/segmentation-mask.xlsx): For metadata entry.
- [📝 TSV template](https://raw.githubusercontent.com/hubmapconsortium/dataset-metadata-spreadsheet/main/segmentation-mask/latest/segmentation-mask.tsv): Alternative for metadata entry.


[EPIC Overview Page](https://docs.google.com/document/d/1-zGHR-seAH-_RT-P4GZmyui0CsxPenKNb5A2FvcRxYQ/)
**Obj x feature table**
1. **Download the Excel [obj x feature template](https://github.com/hubmapconsortium/dataset-metadata-spreadsheet/raw/refs/heads/main/epic/latest/segmentation-mask-object-by-feature.xlsx)**
2. **[Review documentation and examples](https://docs.google.com/document/d/1LgQ509UOoZsY-sZO1cBFtqxWbo3jLGyCVy-_mssBVMw)**
3. **Fill out the Excel obj x feature template for your dataset and submit.**

## Metadata schema


<summary><a href="https://openview.metadatacenter.org/templates/https:%2F%2Frepo.metadatacenter.org%2Ftemplates%2F271bdcd3-b4ac-48e0-ac0f-d666652988af"><b>Version 2 (use this one)</b></a></summary>



<br>

## Directory schemas
<summary><b>Version 2.6 (use this one)</b></summary>

| pattern | required? | description |
| --- | --- | --- |
| <code>extras\/.*</code> | ✓ | Folder for general lab-specific files related to the dataset. |
| <code>derived\/.*</code> | ✓ | The EPIC data is placed in TOP/derived/ so it does not conflict with any files if it is uploaded with a primary dataset. |
| <code>derived\/extras\/.*</code> | ✓ | Folder for general lab-specific files related to the derived dataset. |
| <code>derived\/segmentation_masks\/.*</code> | ✓ | Directory containing segmentation masks. |
| <code>derived\/segmentation_masks\/[^\/]+\.segmentations\.ome\.tiff$</code> | ✓ | The segmentation masks should be stored as multi-channel pyramidal OME TIFF bitmasks with one channel per mask, where a single mask contains all instances of a type of object (e.g., all cells, a class of FTUs, etc). The class of objects contained in the mask is documented in the segmentation-masks.csv file. Each individual object in a mask should be represented by a unique integer pixel value starting at 1, with 0 meaning background (e.g., all pixels belonging to the first instance of a T-cell have a value of 1, the pixels for the second instance of a T-cell have a value of 2, etc). The pixel values should be unique within a mask. FTUs and other structural elements should be captured the same way as cells with segmentation masks and the appropriate channel feature definitions. |
| <code>derived\/segmentation_masks\/[^\/]+-objects\.xlsx$</code> | ✓ | This is a matrix where each row describes an individual object (e.g., one row per cell in the case where a mask contains all cells) and columns are features (i.e., object type, marker intensity, classification strategies, etc). One file should be created per mask with the name of the mask prepended to the file name. For example, if there is a cell segmentation map called “cells” then you would include a file called “cells-objects.xlsx” and that file would contain one row per cell in the “cells” mask and one column per feature, such as marker intensity and/or cell type. |
| <code>derived\/segmentation_masks\/[^\/]+-centroid-adjacency\.csv$</code> |  | Objects are required to be in the same mask. A separate centroid-adjacency file can be included per mask. |
| <code>derived\/segmentation_masks\/[^\/]+-linkage-adjacency\.csv$</code> |  | Objects are required to be in the same mask. A separate linkage-adjacency file can be included per mask. |
| <code>derived\/segmentation_masks\/[^\/]+-mesh\.glb$</code> |  | This is a file with 3D mesh images for a 3D map. |
| <code>derived\/segmentation_masks\/transformations\/.*</code> |  | This directory should include any transformation files that pertain to a 3D reconstruction from serial sections. The mask protocol should explain the structure of these transformation files and how they can be used to reconstruct the 3D map from the 2D sections. |

<summary><b>Version 2.5</b></summary>

| pattern | required? | description |
| --- | --- | --- |
| <code>extras\/.*</code> | ✓ | Folder for general lab-specific files related to the dataset. |
| <code>derived\/.*</code> | ✓ | The EPIC data is placed in TOP/derived/ so it does not conflict with any files if it is uploaded with a primary dataset. |
| <code>derived\/extras\/.*</code> | ✓ | Folder for general lab-specific files related to the derived dataset. |
| <code>derived\/segmentation_masks\/.*</code> | ✓ | Directory containing segmentation masks. |
| <code>derived\/segmentation_masks\/[^\/]+\.segmentations\.ome\.(?:tif&#124;tiff)$</code> | ✓ | The segmentation masks should be stored as multi-channel pyramidal OME TIFF bitmasks with one channel per mask, where a single mask contains all instances of a type of object (e.g., all cells, a class of FTUs, etc). The class of objects contained in the mask is documented in the segmentation-masks.csv file. Each individual object in a mask should be represented by a unique integer pixel value starting at 1, with 0 meaning background (e.g., all pixels belonging to the first instance of a T-cell have a value of 1, the pixels for the second instance of a T-cell have a value of 2, etc). The pixel values should be unique within a mask. FTUs and other structural elements should be captured the same way as cells with segmentation masks and the appropriate channel feature definitions. |
| <code>derived\/segmentation_masks\/[^\/]+-objects\.xlsx$</code> | ✓ | This is a matrix where each row describes an individual object (e.g., one row per cell in the case where a mask contains all cells) and columns are features (i.e., object type, marker intensity, classification strategies, etc). One file should be created per mask with the name of the mask prepended to the file name. For example, if there is a cell segmentation map called “cells” then you would include a file called “cells-objects.xlsx” and that file would contain one row per cell in the “cells” mask and one column per feature, such as marker intensity and/or cell type. |
| <code>derived\/segmentation_masks\/[^\/]+-centroid-adjacency\.csv$</code> |  | Objects are required to be in the same mask. A separate centroid-adjacency file can be included per mask. |
| <code>derived\/segmentation_masks\/[^\/]+-linkage-adjacency\.csv$</code> |  | Objects are required to be in the same mask. A separate linkage-adjacency file can be included per mask. |
| <code>derived\/segmentation_masks\/[^\/]+-mesh\.glb$</code> |  | This is a file with 3D mesh images for a 3D map. |
| <code>derived\/segmentation_masks\/transformations\/.*</code> |  | This directory should include any transformation files that pertain to a 3D reconstruction from serial sections. The mask protocol should explain the structure of these transformation files and how they can be used to reconstruct the 3D map from the 2D sections. |

<summary><b>Version 2.4</b></summary>

| pattern | required? | description |
| --- | --- | --- |
| <code>extras\/.*</code> | ✓ | Folder for general lab-specific files related to the dataset. |
| <code>derived\/.*</code> | ✓ | The EPIC data is placed in TOP/derived/ so it does not conflict with any files if it is uploaded with a primary dataset. |
| <code>derived\/extras\/.*</code> | ✓ | Folder for general lab-specific files related to the derived dataset. |
| <code>derived\/segmentation_masks\/.*</code> | ✓ | Directory containing segmentation masks. |
| <code>derived\/segmentation_masks\/[^\/]+\.segmentations\.ome\.tiff$</code> | ✓ | The segmentation masks should be stored as multi-channel pyramidal OME TIFF bitmasks with one channel per mask, where a single mask contains all instances of a type of object (e.g., all cells, a class of FTUs, etc). The class of objects contained in the mask is documented in the segmentation-masks.csv file. Each individual object in a mask should be represented by a unique integer pixel value starting at 1, with 0 meaning background (e.g., all pixels belonging to the first instance of a T-cell have a value of 1, the pixels for the second instance of a T-cell have a value of 2, etc). The pixel values should be unique within a mask. FTUs and other structural elements should be captured the same way as cells with segmentation masks and the appropriate channel feature definitions. |
| <code>derived\/segmentation_masks\/[^\/]+-objects\.xlsx$</code> | ✓ | This is a matrix where each row describes an individual object (e.g., one row per cell in the case where a mask contains all cells) and columns are features (i.e., object type, marker intensity, classification strategies, etc). One file should be created per mask with the name of the mask prepended to the file name. For example, if there is a cell segmentation map called “cells” then you would include a file called “cells-objects.xlsx” and that file would contain one row per cell in the “cells” mask and one column per feature, such as marker intensity and/or cell type. |
| <code>derived\/segmentation_masks\/[^\/]+-centroid-adjacency\.csv$</code> |  | Objects are required to be in the same mask. A separate centroid-adjacency file can be included per mask. |
| <code>derived\/segmentation_masks\/[^\/]+-linkage-adjacency\.csv$</code> |  | Objects are required to be in the same mask. A separate linkage-adjacency file can be included per mask. |
| <code>derived\/segmentation_masks\/[^\/]+-mesh\.glb$</code> |  | This is a file with 3D mesh images for a 3D map. |
| <code>derived\/segmentation_masks\/transformations\/.*</code> |  | This directory should include any transformation files that pertain to a 3D reconstruction from serial sections. The mask protocol should explain the structure of these transformation files and how they can be used to reconstruct the 3D map from the 2D sections. |

<summary><b>Version 2.3</b></summary>

| pattern | required? | description |
| --- | --- | --- |
| <code>extras\/.*</code> | ✓ | Folder for general lab-specific files related to the dataset. |
| <code>derived\/.*</code> | ✓ | The EPIC data is placed in TOP/derived/ so it does not conflict with any files if it is uploaded with a primary dataset. |
| <code>derived\/extras\/.*</code> | ✓ | Folder for general lab-specific files related to the derived dataset. |
| <code>derived\/segmentation_masks\/.*</code> | ✓ | Directory containing segmentation masks. |
| <code>derived\/segmentation_masks\/[^\/]+\.segmentations\.ome\.tiff$</code> | ✓ | The segmentation masks should be stored as multi-channel pyramidal OME TIFF bitmasks with one channel per mask, where a single mask contains all instances of a type of object (e.g., all cells, a class of FTUs, etc). The class of objects contained in the mask is documented in the segmentation-masks.csv file. Each individual object in a mask should be represented by a unique integer pixel value starting at 1, with 0 meaning background (e.g., all pixels belonging to the first instance of a T-cell have a value of 1, the pixels for the second instance of a T-cell have a value of 2, etc). The pixel values should be unique within a mask. FTUs and other structural elements should be captured the same way as cells with segmentation masks and the appropriate channel feature definitions. |
| <code>derived\/segmentation_masks\/[^\/]+-objects\.(?:tsv&#124;xlsx)$</code> | ✓ | This is a matrix where each row describes an individual object (e.g., one row per cell in the case where a mask contains all cells) and columns are features (i.e., object type, marker intensity, classification strategies, etc). One file should be created per mask with the name of the mask prepended to the file name. For example, if there is a cell segmentation map called "cells" then you would include a file called "cells-objects.csv" and that file would contain one row per cell in the "cells" mask and one column per feature, such as marker intensity and/or cell type. A minimum set of fields (required and optional) is included below. |
| <code>derived\/segmentation_masks\/[^\/]+-centroid-adjacency\.csv$</code> |  | Objects are required to be in the same mask. A separate centroid-adjacency file can be included per mask. |
| <code>derived\/segmentation_masks\/[^\/]+-linkage-adjacency\.csv$</code> |  | Objects are required to be in the same mask. A separate linkage-adjacency file can be included per mask. |
| <code>derived\/segmentation_masks\/[^\/]+-mesh\.glb$</code> |  | This is a file with 3D mesh images for a 3D map. |
| <code>derived\/segmentation_masks\/transformations\/.*</code> |  | This directory should include any transformation files that pertain to a 3D reconstruction from serial sections. The mask protocol should explain the structure of these transformation files and how they can be used to reconstruct the 3D map from the 2D sections. |

<summary><b>Version 2.2</b></summary>

| pattern | required? | description |
| --- | --- | --- |
| <code>extras\/.*</code> | ✓ | Folder for general lab-specific files related to the dataset. |
| <code>derived\/.*</code> | ✓ | The EPIC data is placed in TOP/derived/ so it does not conflict with any files if it is uploaded with a primary dataset. |
| <code>derived\/extras\/.*</code> | ✓ | Folder for general lab-specific files related to the derived dataset. |
| <code>derived\/segmentation_masks\/.*</code> | ✓ | Directory containing segmentation masks. |
| <code>derived\/segmentation_masks\/[^\/]+\.segmentations\.ome\.tiff</code> | ✓ | The segmentation masks should be stored as multi-channel pyramidal OME TIFF bitmasks with one channel per mask, where a single mask contains all instances of a type of object (e.g., all cells, a class of FTUs, etc). The class of objects contained in the mask is documented in the segmentation-masks.csv file. Each individual object in a mask should be represented by a unique integer pixel value starting at 1, with 0 meaning background (e.g., all pixels belonging to the first instance of a T-cell have a value of 1, the pixels for the second instance of a T-cell have a value of 2, etc). The pixel values should be unique within a mask. FTUs and other structural elements should be captured the same way as cells with segmentation masks and the appropriate channel feature definitions. |
| <code>derived\/segmentation_masks\/[^\/]+-objects\.(?:tsv&#124;xlsx)</code> | ✓ | This is a matrix where each row describes an individual object (e.g., one row per cell in the case where a mask contains all cells) and columns are features (i.e., object type, marker intensity, classification strategies, etc). One file should be created per mask with the name of the mask prepended to the file name. For example, if there is a cell segmentation map called "cells" then you would include a file called "cells-objects.csv" and that file would contain one row per cell in the "cells" mask and one column per feature, such as marker intensity and/or cell type. A minimum set of fields (required and optional) is included below. |
| <code>derived\/segmentation_masks\/[^\/]+-centroid-adjacency\.csv</code> |  | Objects are required to be in the same mask. A separate centroid-adjacency file can be included per mask. |
| <code>derived\/segmentation_masks\/[^\/]+-linkage-adjacency\.csv</code> |  | Objects are required to be in the same mask. A separate linkage-adjacency file can be included per mask. |
| <code>derived\/segmentation_masks\/[^\/]+-mesh\.glb</code> |  | This is a file with 3D mesh images for a 3D map. |
| <code>derived\/segmentation_masks\/transformations\/.*</code> |  | This directory should include any transformation files that pertain to a 3D reconstruction from serial sections. The mask protocol should explain the structure of these transformation files and how they can be used to reconstruct the 3D map from the 2D sections. |

<summary><b>Version 2.1</b></summary>

| pattern | required? | description |
| --- | --- | --- |
| <code>derived\/.*</code> | ✓ | The EPIC data is placed in TOP/derived/ so it does not conflict with any files if it is uploaded with a primary dataset. |
| <code>derived\/extras\/.*</code> | ✓ | Folder for general lab-specific files related to the derived dataset. |
| <code>derived\/segmentation_masks\/.*</code> | ✓ | Directory containing segmentation masks. |
| <code>derived\/segmentation_masks\/[^\/]+\.segmentations\.ome\.tiff</code> | ✓ | The segmentation masks should be stored as multi-channel pyramidal OME TIFF bitmasks with one channel per mask, where a single mask contains all instances of a type of object (e.g., all cells, a class of FTUs, etc). The class of objects contained in the mask is documented in the segmentation-masks.csv file. Each individual object in a mask should be represented by a unique integer pixel value starting at 1, with 0 meaning background (e.g., all pixels belonging to the first instance of a T-cell have a value of 1, the pixels for the second instance of a T-cell have a value of 2, etc). The pixel values should be unique within a mask. FTUs and other structural elements should be captured the same way as cells with segmentation masks and the appropriate channel feature definitions. |
| <code>derived\/segmentation_masks\/[^\/]+-objects\.(?:tsv&#124;xlsx)</code> | ✓ | This is a matrix where each row describes an individual object (e.g., one row per cell in the case where a mask contains all cells) and columns are features (i.e., object type, marker intensity, classification strategies, etc). One file should be created per mask with the name of the mask prepended to the file name. For example, if there is a cell segmentation map called "cells" then you would include a file called "cells-objects.csv" and that file would contain one row per cell in the "cells" mask and one column per feature, such as marker intensity and/or cell type. A minimum set of fields (required and optional) is included below. |
| <code>derived\/segmentation_masks\/[^\/]+-centroid-adjacency\.csv</code> |  | Objects are required to be in the same mask. A separate centroid-adjacency file can be included per mask. |
| <code>derived\/segmentation_masks\/[^\/]+-linkage-adjacency\.csv</code> |  | Objects are required to be in the same mask. A separate linkage-adjacency file can be included per mask. |
| <code>derived\/segmentation_masks\/[^\/]+-mesh\.glb</code> |  | This is a file with 3D mesh images for a 3D map. |
| <code>derived\/segmentation_masks\/transformations\/.*</code> |  | This directory should include any transformation files that pertain to a 3D reconstruction from serial sections. The mask protocol should explain the structure of these transformation files and how they can be used to reconstruct the 3D map from the 2D sections. |

<summary><b>Version 2.0</b></summary>

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

