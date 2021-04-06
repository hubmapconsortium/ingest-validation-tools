# contributors

Related files:

- [📝 Excel template](https://raw.githubusercontent.com/hubmapconsortium/ingest-validation-tools/master/docs/contributors/contributors.xlsx): For metadata entry.
- [📝 TSV template](https://raw.githubusercontent.com/hubmapconsortium/ingest-validation-tools/master/docs/contributors/contributors.tsv): Alternative for metadata entry.





## Metadata schema


<details open="true"><summary><b>Version 1 (current)</b></summary>

<blockquote>

[`version`](#version)<br>
[`affiliation`](#affiliation)<br>
[`first_name`](#first_name)<br>
[`last_name`](#last_name)<br>
[`middle_name_or_initial`](#middle_name_or_initial)<br>
[`name`](#name)<br>
[`orcid_id`](#orcid_id)<br>
[`is_contact`](#is_contact)<br>

</blockquote>

##### `version`
Version of the schema to use when validating this metadata.
| constraint | value |
| --- | --- |
| enum | `1` |
| required | `True` |

##### `affiliation`
Institutional affiliation.
| constraint | value |
| --- | --- |
| required | `True` |

##### `first_name`
First name.
| constraint | value |
| --- | --- |
| required | `True` |

##### `last_name`
Last name.
| constraint | value |
| --- | --- |
| required | `True` |

##### `middle_name_or_initial`
Middle name or initial. Leave blank if not applicable.
| constraint | value |
| --- | --- |
| required | `False` |

##### `name`
Name for display.
| constraint | value |
| --- | --- |
| required | `True` |

##### `orcid_id`
ORCID ID of contributor. Example: `0000-0002-8928-741X`.
| constraint | value |
| --- | --- |
| pattern (regular expression) | `\d{4}-\d{4}-\d{4}-\d{3}[0-9X]` |
| required | `True` |
| url | prefix: `https://orcid.org/` |

##### `is_contact`
Is this individual a contact for DOI purposes?
| constraint | value |
| --- | --- |
| type | `boolean` |
| required | `True` |

</details>


<details ><summary><b>Version 0</b></summary>


##### `affiliation`
Institutional affiliation.
| constraint | value |
| --- | --- |
| required | `True` |

##### `first_name`
First name.
| constraint | value |
| --- | --- |
| required | `True` |

##### `last_name`
Last name.
| constraint | value |
| --- | --- |
| required | `True` |

##### `middle_name_or_initial`
Middle name or initial. Leave blank if not applicable.
| constraint | value |
| --- | --- |
| required | `False` |

##### `name`
Name for display.
| constraint | value |
| --- | --- |
| required | `True` |

##### `orcid_id`
ORCID ID of contributor. Example: `0000-0002-8928-741X`.
| constraint | value |
| --- | --- |
| pattern (regular expression) | `\d{4}-\d{4}-\d{4}-\d{3}[0-9X]` |
| required | `True` |
| url | prefix: `https://orcid.org/` |

</details>
