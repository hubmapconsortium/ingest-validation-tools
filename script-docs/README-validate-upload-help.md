This document lists common `validate_upload.py` errors, their interpretation, and their remedies.

## `404` error
```
row 22, protocols_io_doi 10.17504/protocols.io.be8mjhu7: 404
```

### Description
Certain fields require entities that end in a number or letter. If the entity is a DOI, and you have dragged the contents from the cell in row 2 down to fill the rows below, the number or letter at the end of the entity will increase incrementally. DOIs will generate 404 errors because the resulting DOIs are not valid (hopefully).

### Remedy
If every row in the document is meant to contain precisely the same entity, then the entity can be copied from one cell, which saves it on a clipboard. Highlight the cells which should contain a copy and paste the entity into those cells.

## Is not “datetime” and format
```
The value "12/23/20 12:00" in row 2 and column 3 ("C") is not type "datetime
and format "%Y-%m-%d %H:%M"
```

### Description
The metadata documentation for each assay in github describes input for each field. 
In most cases, input is required. In many cases, the format is constrained. Datetime and date are two examples of fields in which input is required in a constrained format.  If the user is populating these fields in excel, the datetime input must be specifically formatted as follows:
- `yyyy-mm-dd hh:mm` (e.g. where required input is datetime)
- `yyyy-mm-dd` (where required input is date - e.g. in the lot_number field for custom antibodies in the antibodies TSV).

### Remedy
In Excel, highlight the column and in "Format Cells" select "Custom" and give 
`yyyy-mm-dd hh:mm` as the format.
This reformatting is required every time you modify the document in Excel 


