```
Upload Errors:
  Directory Errors:
    ? examples/dataset-examples/bad-cedar-multi-assay-visium-bad-child-metadata/upload/good-visium-assay-metadata.tsv,
      column 'data_path', value ./Visium_9OLC_A4_S1
    : Draft directory schema: visium-no-probes-v2
    ? examples/dataset-examples/bad-cedar-multi-assay-visium-bad-child-metadata/upload/good-visium-assay-metadata.tsv,
      column 'data_path', value ./Visium_9OLC_A4_S2
    : Draft directory schema: visium-no-probes-v2
    ? examples/dataset-examples/bad-cedar-multi-assay-visium-bad-child-metadata/upload/good-visium-assay-metadata.tsv,
      column 'data_path', value ./Visium_9OLC_I4_S1
    : Draft directory schema: visium-no-probes-v2
Metadata TSV Validation Errors:
  CEDAR Validation Errors:
    examples/dataset-examples/bad-cedar-multi-assay-visium-bad-child-metadata/upload/bad-visium-rnaseq-metadata.tsv:
      URL Errors:
      - 'Row 3, field "parent_sample_id" with value "": 404 Client Error: Not Found
        for url: https://entity.api.hubmapconsortium.org/entities/.'
      Request Errors:
        message: Failed to populate categorical values for the "sequencing_reagent_kit"
          field.
        cause: 'Bad request to /bioportal/integrated-search.

          POST https://terminology.metadatacenter.org/bioportal/integrated-search/
          HTTP/1.1

          {"parameterObject":{"valueConstraints":{"ontologies":[],"valueSets":[],"classes":[],"branches":[{"uri":"https://purl.humanatlas.io/vocab/hravs#HRAVS_1001081","source":"undefined
          (HRAVS)","acronym":"HRAVS","name":"Sequencing reagent kit","maxDepth":0}],"actions":[],"defaultValue":null,"requiredValue":true}},"pageSize":5000,"page":1}.'
        statusInfo: 429 Too Many Requests.
        fixSuggestion: ''
Hint: 'If validation fails because of extra whitespace in the TSV, try:

  src/cleanup_whitespace.py --tsv_in original.tsv --tsv_out clean.tsv.'
```
