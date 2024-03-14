---
title: murine-source
schema_name: murine-source
category: Other TSVs
all_versions_deprecated: False
exclude_from_index: False
layout: default
---

Related files:

- [📝 Excel template](https://raw.githubusercontent.com/hubmapconsortium/ingest-validation-tools/main/docs/murine-source/murine-source.xlsx): For metadata entry.
- [📝 TSV template](https://raw.githubusercontent.com/hubmapconsortium/ingest-validation-tools/main/docs/murine-source/murine-source.tsv): Alternative for metadata entry.







## Metadata schema

### Field types
- *Boolean* fields can be given as `TRUE`/`FALSE`, `True`/`False`, `true`/`false`, or `1`/`0`.  


<details markdown="1" open="true"><summary><b>Version 0 (current)</b></summary>

<blockquote markdown="1">

[`source_id`](#source_id)<br>
[`strain`](#strain)<br>
[`strain_rrid`](#strain_rrid)<br>
[`sex`](#sex)<br>
[`is_embryo`](#is_embryo)<br>
[`date_of_birth_or_fertilization`](#date_of_birth_or_fertilization)<br>
[`is_deceased`](#is_deceased)<br>
[`date_of_death`](#date_of_death)<br>
[`euthanization_method`](#euthanization_method)<br>
[`local_lifespan_data`](#local_lifespan_data)<br>
[`room_health_status`](#room_health_status)<br>
[`room_temperature`](#room_temperature)<br>
[`rack_setup`](#rack_setup)<br>
[`light_cycle`](#light_cycle)<br>
[`bedding`](#bedding)<br>
[`diet`](#diet)<br>
[`water_source`](#water_source)<br>
[`cage_enhancements`](#cage_enhancements)<br>

</blockquote>

<a name="source_id"></a>
##### [`source_id`](#source_id)
SenNet ID of the source (whole organism) of the assayed tissue. Leave blank if not applicable. Example: `SNT123.ABCD.567`.

| constraint | value |
| --- | --- |
| required | `False` |
| pattern (regular expression) | <code>[SNT]+\d{3}\.[A-Za-z]{4}\.\d{3}</code> |

<a name="strain"></a>
##### [`strain`](#strain)
Jackson Labs nomenclature. When mutant alleles are part of the strain name, use "<" and ">" to indicate the superscripted alleles. For example, C57BL/6J-KitW-39J should be entered as "C57BL/6J-Kit<W-39J>", where "W-39J" would be the portion of the string displayed as superscripted text. For further information, see the "Quick Guide to Mouse Nomenclature" (https://resources.jax.org/guides/quick-guide-to-mouse-nomenclature).

| constraint | value |
| --- | --- |
| required | `True` |

<a name="strain_rrid"></a>
##### [`strain_rrid`](#strain_rrid)
The Research Resource Identifier (RRID) (https://scicrunch.org/resources/data/source/nlx_154697-1/search) for the strain. An example is 'RRID:MGI:3713213'.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="sex"></a>
##### [`sex`](#sex)
The sex of the mouse.

| constraint | value |
| --- | --- |
| required | `True` |
| enum | `M` or `F` |

<a name="is_embryo"></a>
##### [`is_embryo`](#is_embryo)
Is the source an embryo? Use either 'True' or 'False'.

| constraint | value |
| --- | --- |
| type | `boolean` |
| required | `True` |

<a name="date_of_birth_or_fertilization"></a>
##### [`date_of_birth_or_fertilization`](#date_of_birth_or_fertilization)
The date when the mouse/embryo was born/fertilized. If the hours/minutes are not known, use '00:00'.

| constraint | value |
| --- | --- |
| type | `datetime` |
| format | `%Y-%m-%d %H:%M` |
| required | `True` |

<a name="is_deceased"></a>
##### [`is_deceased`](#is_deceased)
Is the source deceased? Use either 'True' or 'False'.

| constraint | value |
| --- | --- |
| type | `boolean` |
| required | `True` |

<a name="date_of_death"></a>
##### [`date_of_death`](#date_of_death)
The date when the mouse/embryo died. If the hours/minutes are not known, use '00:00'. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| type | `datetime` |
| format | `%Y-%m-%d %H:%M` |
| required | `False` |

<a name="euthanization_method"></a>
##### [`euthanization_method`](#euthanization_method)
If the source was euthanized, select the method of euthanization. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |
| enum | `Carbon dioxide asphixiation`, `Inhaled anesthetic agents`, `Injected anesthetic agents`, `Cervical dislocation`, `Decapitation`, `Hypothermia`, `Rapid freezing`, or `Other` |

<a name="local_lifespan_data"></a>
##### [`local_lifespan_data`](#local_lifespan_data)
A free text description of how long mice live within the local environment. It is recommended to provide the median or maximum values for murine lifespans. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |

<a name="room_health_status"></a>
##### [`room_health_status`](#room_health_status)
A description of the pathogen and opportunist exclusion level of the room where the source is housed. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |
| enum | `Pathogen free`, `Pathogen and opportunist free`, or `Other` |

<a name="room_temperature"></a>
##### [`room_temperature`](#room_temperature)
The temperature value in Celsius of the room where the source is housed. An example is "23". Leave blank if not applicable.

| constraint | value |
| --- | --- |
| type | `number` |
| required | `False` |

<a name="rack_setup"></a>
##### [`rack_setup`](#rack_setup)
The rack setup type in which the source is housed. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |
| enum | `Biocontainment`, `Ventilated`, `Micro-Isolator`, or `Conventional` |

<a name="light_cycle"></a>
##### [`light_cycle`](#light_cycle)
The light cycle in the room where the source is housed. "Standard/default" refers to 12-hour photoperiods (e.g., lights on at 7:00 AM, lights off at 7:00 PM). "Longer photoperiods" refers to 14-hour photoperiods (e.g., lights on at 7:00 AM, lights off at 9:00 PM). "Reverse lightcycles" means that the the timing of the 12-hour photoperiod is reversed (.e.g, lights on at 7:00 PM, lights off at 7:00 AM). Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |
| enum | `Standard/default`, `Longer photoperiods`, or `Reverse light cycles` |

<a name="bedding"></a>
##### [`bedding`](#bedding)
The type of cage bedding in the cage where the source is housed. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |
| enum | `Aspen chip`, `Aspen shaving`, `Pine chip`, `Pine shaving`, `1/4-inch corncob`, `1/4-inch pelleted cellulose`, `Refined virgin diced cellulose`, `Non-contact cage board`, `Wire mesh`, or `Other` |

<a name="diet"></a>
##### [`diet`](#diet)
A free text description of the source's diet.

| constraint | value |
| --- | --- |
| required | `True` |

<a name="water_source"></a>
##### [`water_source`](#water_source)
A free text description of the source's water supply, including any treatments to the water. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |

<a name="cage_enhancements"></a>
##### [`cage_enhancements`](#cage_enhancements)
Environmental enrichments present in the source’s cage. Leave blank if not applicable.

| constraint | value |
| --- | --- |
| required | `False` |
| enum | `Nestlets`, `Nest boxes/shelters`, `Shelter tubes`, `Wooden chew sticks`, `Nylon bones`, or `Other` |

</details>

