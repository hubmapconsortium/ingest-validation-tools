---
layout: default
title: HuBMAP Data Upload Guidelines
---

Well-defined schemas ensure that HuBMAP data and metadata are reusable.
If you are starting work on a new assay type, review the
[guidelines for directory schemas](https://github.com/hubmapconsortium/ingest-validation-tools/blob/master/HOWTO-describe-directories.md#readme).
If you have an upload prepared, follow the instructions in 
the [Metadata Validation Workflow](https://docs.google.com/document/d/1lfgiDGbyO4K4Hz1FMsJjmJd9RdwjShtJqFYNwKpbcZY/) 
document to validate your upload.

Assay types and their schemas are linked below.
- [An Excel file](field-schemas.xlsx) listing all the schemas and their fields is available.
- For more information, see the [`ingest-validation-tools` repo](https://github.com/hubmapconsortium/ingest-validation-tools#readme).

{% assign categories = site.pages | group_by: "category" %}
{{ site.categories-order }}
{{ categories }}
{% for category in categories %}
{% unless category.name == "" %}

## {{category.name}}

{% assign pages = category.items | sort: "title" %}
{% for page in pages %}
{% unless page.exclude_from_index %}

{% unless page.all_versions_deprecated %}
- [{{ page.title }}]({{ page.schema_name }})
{% endunless %}

{% endunless %}
{% endfor %}

{% endunless %}
{% endfor %}
