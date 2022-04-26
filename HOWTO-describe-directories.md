# How to describe directories

There are several reasons to precisely define the directory structures of datasets:

- So curent and future data providers know what they are expected to submit.
- So HIVE pipeline creators know what they can expect to receive.
- So future data users are able to make the best use of the data.

A good directory description should satisfy everyone.

All teams that will be submitting a given assay type should be at the table,
since the final specification will apply to everyone.
Each team should run `find .` in a local dataset directory to provide an example of their current structure,
but teams should expect to make changes to their workflows to arrive at a consensus structure.
A table like this provides the information the developers need to know: (Example is from CODEX.)

| Path | Example | Description | is QA? | is optional? |
| ---- | ------- | ----------- | ------ | ------------ |
| `experiment.json`   | | Metadata for the experiment ... |    |          |
| `*.pdf`             | | Image analysis report ...       | QA |          |
| `cyc*_reg*_*/*.gci` | `cyc01_reg01_123/abc123.gci` | Group capture information ...   |    | optional |

- The `Path` gives the directory and the file name where the file will be found.
  If parts of the path are variable, use `*`, or to be more precise, use regular expressions.
- An `Example` can be useful, particularly if the path is flexible. 
- The `Description` describes what a file does. A sentance or two is good; Don't just repeat the extension!
If CSV, what are the columns? If JSON, is there a schema?
- If the file is used for QA, make that clear.
- If the file is optional, make that clear.

## How to make it flexible, and how flexible to make it

Even when a file is "required", it only means that there is at least one match:
`*/data.csv` is satisfied if `x/data.csv` exists in the dataset, even if `y/` and `z/` do not contain a `data.csv`. 

Regular expression syntax is used internally, and it is more expressive than the glob matches.
One feature is alternations: `abc\.txt|xyz\.txt` will match either `abc.txt` or `xyz.txt`.
Character classes can be used if there are patterns in filenames:
`[A-Z]+\d+\.txt` will match either `K9.txt` or `UNGUL8.txt` but not `2CAN.txt`.

Extra files can be dropped in the `extras/` directory and they will not cause validation errors...
but if it could be useful to someone in the future, let's try to get a description so they know about it.

## What makes a good directory structure

In general:
- Don't use proprietary formats: For plain text, use TXT instead of a Word document.
- Use formats which are easier to reuse: Instead of a PDF report, consider HTML.
- For a CSV or TSV, what are the columns?
- For JSON or XML, is there a schema or other outside reference?
- Use `ome.tiff` for raster data.
- Don't use spaces in filenames.
- Don't use mixed case in filenames.
- For `.zip` or `.gz`, include the original extension along with the new one. For example, `data.csv.gz`, and not just `data.gz`.
