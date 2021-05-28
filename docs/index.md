---
layout: default
title: HuBMAP Data Upload Guidelines
---

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
