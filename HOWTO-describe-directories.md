# How to describe directories.

In order to confirm that the correct files have been submitted, we need to know what to expect.
A table like this provides the information the developers need to know: (Example is from CODEX.)

| Path | Description | is QA? | is optional? |
| ---- | ----------- | ------ | ------------ |
| `experiment.json`   | Metadata for the experiment ... |    |          |
| `*.pdf`             | Image analysis report ...       | QA |          |
| `cyc*_reg*_*/*.gci` | Group capture information ...   |    | optional |

- The `Path` gives the directory and the file name where the file will be found.
  If parts of the path are variable, use `*`, or to be more precise, use regular expressions.
- The `Description` describes what a file does. A sentance or two is good; Don't just repeat the extension!
- If the file is used for QA, make that clear.
- If the file is optional, make that clear.

If you have more loosely structured information you'd like to provide,
it can be in an `extras/` directory in the dataset.

If the files are coming from third party software, just describe the outputs.
If you have control over the output, here are some best practices:
- Don't use proprietary formats. If it's a table of numbers, provide a CSV or TSV instead of Excel.
- Use `ome.tiff` for raster data. If you have a preview image, provide it at `extras/thumbnail.{png,jpg}`
- Use simple consistent filenames. Best to avoid spaces in filenames, and all lowercase is usually preferable to mixed-case.