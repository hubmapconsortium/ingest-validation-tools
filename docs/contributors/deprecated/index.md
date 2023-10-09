---
title: contributors
schema_name: contributors
category: Other TSVs
all_versions_deprecated: False
exclude_from_index: False
layout: default
---

Related files:


- [📝 Excel template](https://raw.githubusercontent.com/hubmapconsortium/ingest-validation-tools/main/docs/contributors/contributors.xlsx): For metadata entry.
- [📝 TSV template](https://raw.githubusercontent.com/hubmapconsortium/ingest-validation-tools/main/docs/contributors/contributors.tsv): Alternative for metadata entry.




## Metadata schema


<details markdown="1" open="true"><summary><b>Version 1 (use this one)</b></summary>

<blockquote markdown="1">

[`version`](#version)<br>
[`affiliation`](#affiliation)<br>
[`first_name`](#first_name)<br>
[`last_name`](#last_name)<br>
[`middle_name_or_initial`](#middle_name_or_initial)<br>
[`name`](#name)<br>
[`orcid_id`](#orcid_id)<br>
[`is_contact`](#is_contact)<br>

</blockquote>

<a name="version"></a>
##### [`version`](#version)
Version of the schema to use when validating this metadata.

| constraint | value |
| --- | --- |
| enum | `1` |
| required | `True` |

<a name="affiliation"></a>
##### [`affiliation`](#affiliation)
Institutional affiliation.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="first_name"></a>
##### [`first_name`](#first_name)
First name.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="last_name"></a>
##### [`last_name`](#last_name)
Last name.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="middle_name_or_initial"></a>
##### [`middle_name_or_initial`](#middle_name_or_initial)
Middle name or initial. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |

<a name="name"></a>
##### [`name`](#name)
Name for display.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="orcid_id"></a>
##### [`orcid_id`](#orcid_id)
ORCID ID of contributor. Example: `0000-0002-8928-741X`.

| constraint | value |
| --- | --- |
| pattern (regular expression) | <code>\d{4}-\d{4}-\d{4}-\d{3}[0-9X]</code> |
| required | `True` |
| url | prefix: <code>https://pub.orcid.org/v3.0/</code> |

<a name="is_contact"></a>
##### [`is_contact`](#is_contact)
Is this individual a contact for DOI purposes?

| constraint | value |
| --- | --- |
| type | `boolean` |
| required | `True` |

</details>


<details markdown="1" ><summary><s>Version 0</s> (deprecated)</summary>


<a name="affiliation"></a>
##### [`affiliation`](#affiliation)
Institutional affiliation.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="first_name"></a>
##### [`first_name`](#first_name)
First name.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="last_name"></a>
##### [`last_name`](#last_name)
Last name.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="middle_name_or_initial"></a>
##### [`middle_name_or_initial`](#middle_name_or_initial)
Middle name or initial. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |

<a name="name"></a>
##### [`name`](#name)
Name for display.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="orcid_id"></a>
##### [`orcid_id`](#orcid_id)
ORCID ID of contributor. Example: `0000-0002-8928-741X`.

| constraint | value |
| --- | --- |
| pattern (regular expression) | <code>\d{4}-\d{4}-\d{4}-\d{3}[0-9X]</code> |
| required | `True` |
| url | prefix: <code>https://pub.orcid.org/v3.0/</code> |

</details>


<br>

