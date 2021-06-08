---
layout: default
title: HuBMAP Data Upload Guidelines
---

Well-defined schemas ensure that HuBMAP data and metadata are reusable.
If you are starting work on a new assay type, reivew the
[guidelines for directory schemas](https://github.com/hubmapconsortium/ingest-validation-tools/blob/master/HOWTO-describe-directories.md#readme).
If you have an upload prepared, it can be validated with
[`validate_upload.py`](https://github.com/hubmapconsortium/ingest-validation-tools/blob/master/script-docs/README-validate_upload.py.md#readme),
or if you only have an individual TSV, use [`validate_tsv.py`](https://github.com/hubmapconsortium/ingest-validation-tools/blob/master/script-docs/README-validate_tsv.py.md#readme).
[Examples](https://github.com/hubmapconsortium/ingest-validation-tools/tree/master/examples#dataset-examples) of both good and bad uploads,
and the validation messages they produce, are available.

Assay types and their schemas are linked below; For the bigger picture, and to contribute to this project, see the [`ingest-validation-tools` repo](https://github.com/hubmapconsortium/ingest-validation-tools#readme).

{% assign categories = site.pages | group_by: "category" %}
{% for category in categories %}
{% unless category.name == "" %}

## {{category.name}}

{% assign pages = category.items | sort: "title" %}
{% for page in pages %}
{% unless page.exclude_from_index %}

- [{{ page.title }}]({{ page.schema_name }})

{% endunless %}
{% endfor %}

{% endunless %}
{% endfor %}
