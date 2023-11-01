---
layout: default
title: Current Schemas
---


{% for category-name in site.categories-order %}

## {{ category-name }}

{% assign pages = site.pages | where: "category",category-name | sort: "title" %}

{% for page in pages %}

{% unless page.exclude_from_index %}
{% unless page.all_versions_deprecated %}
{% if page.path contains "current" %}

- [{{ page.title }}](/ingest-validation-tools{{ page.url }})

{% endif %}
{% endunless %}
{% endunless %}
{% endfor %}

{% endfor %}