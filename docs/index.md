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

- [{{ page.title }}]({{ page.schema_name }})

{% endfor %}

{% endunless %}
{% endfor %}
