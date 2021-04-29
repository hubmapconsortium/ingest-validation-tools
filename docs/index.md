---
# Feel free to add content and custom Front Matter to this file.
# To modify the layout, see https://jekyllrb.com/docs/themes/#overriding-theme-defaults

layout: default
title: HuBMAP Data Submission Guidelines
---

{% assign pages_az = site.pages | sort: "title" %}
{% for p in pages_az %}
{% unless p.title == page.title or p.title == nil %}
[{{ p.title }}]({{ p.title }})
{% endunless %}
{% endfor %}