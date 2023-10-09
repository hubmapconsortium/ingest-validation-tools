---
layout: default
title: Deprecated Schemas
---

{% assign categories = "" | split: ',' %}
{% for page in site.pages %}
{% if page.path contains "deprecated" %}
{% assign categories = categories | push: page.category %}
{% endif %}
{% endfor %}

{% assign categories = categories | uniq %}

{% for category-name in categories %}
{% if category-name %}

## {{category-name}}

{% assign pages = site.pages | where: "category",category-name | sort: "title" %}

{% for page in pages %}
{% unless page.exclude_from_index %}

{% unless page.all_versions_deprecated %}
{% if page.path contains "deprecated" %}

- [{{ page.title }}](/ingest-validation-tools{{ page.url }})

{% endif %}
{% endunless %}

{% endunless %}
{% endfor %}

{% endif %}
{% endfor %}