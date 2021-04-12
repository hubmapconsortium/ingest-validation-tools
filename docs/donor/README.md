# donor

Related files:

- [📝 Excel template](https://raw.githubusercontent.com/hubmapconsortium/ingest-validation-tools/master/docs/donor/donor.xlsx): For metadata entry.
- [📝 TSV template](https://raw.githubusercontent.com/hubmapconsortium/ingest-validation-tools/master/docs/donor/donor.tsv): Alternative for metadata entry.

This file is really only here to provide descriptions of fields in the UI. The full description of Donor metadata is at https://portal.hubmapconsortium.org/docs/donor
Most definitions taken from https://ncit.nci.nih.gov/ncitbrowser/pages/home.jsf?version=20.11e



## Metadata schema


<details open="true"><summary><b>Version 0 (current)</b></summary>

<blockquote>

[`age_value`](#age_value)<br>
[`blood_type`](#blood_type)<br>
[`body_mass_index_value`](#body_mass_index_value)<br>
[`cause_of_death`](#cause_of_death)<br>
[`height_unit`](#height_unit)<br>
[`kidney_donor_profile_index_value`](#kidney_donor_profile_index_value)<br>
[`mechanism_of_injury`](#mechanism_of_injury)<br>
[`medical_history`](#medical_history)<br>
[`race`](#race)<br>
[`sex`](#sex)<br>
[`weight_value`](#weight_value)<br>

</blockquote>

##### `age_value`
The time elapsed since birth.
| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

##### `blood_type`
ABO blood type or "serotype" refers to the presence/absence of the either/both A & B blood antigens.
| constraint | value |
| --- | --- |
| required | `True` |

##### `body_mass_index_value`
An individual's weight in kilograms divided by the square of the height in meters.
| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

##### `cause_of_death`
The circumstance or condition that caused death.
| constraint | value |
| --- | --- |
| required | `True` |

##### `height_unit`
The vertical measurement or distance from the base to the top of a subject or participant.
| constraint | value |
| --- | --- |
| required | `True` |

##### `kidney_donor_profile_index_value`
The Kidney Donor Profle Index (KDPI) is a numerical measure that combines ten donor factors, including clinical parameters and demographics, to summarize into a single number the quality of deceased donor kidneys relative to other recovered kidneys. The KDPI is derived by frst calculating the Kidney Donor Risk Index (KDRI) for a deceased donor. Kidneys from a donor with a KDPI of 90%, for example, have a KDRI (which indicates relative risk of graft failure) greater than 90% of recovered kidneys. The KDPI is simply a mapping of the KDRI from a relative risk scale to a cumulative percentage scale. The reference population used for this mapping is all deceased donors in the United States  with a kidney recovered for the purpose of transplantation in the prior calendar year.  Lower KDPI values are associated with increased donor quality and expected longevity. https://optn.transplant.hrsa.gov/media/1512/guide_to_calculating_interpreting_kdpi.pdf.
| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

##### `mechanism_of_injury`
Mechanism of injury may be, for example: fall, impact (eg: auto accident), weapon (eg: firearm), etc.
| constraint | value |
| --- | --- |
| required | `True` |

##### `medical_history`
A record of a patient's background regarding health and the occurrence of disease events of the individual.
| constraint | value |
| --- | --- |
| required | `True` |

##### `race`
A grouping of humans based on shared physical characteristics or social/ethnic identity generally viewed as distinct.
| constraint | value |
| --- | --- |
| required | `True` |

##### `sex`
Biological sex at birth: male or female or other.
| constraint | value |
| --- | --- |
| required | `True` |

##### `weight_value`
A measurement that describes the vertical force exerted by a mass of the patient as a result of gravity.
| constraint | value |
| --- | --- |
| type | `number` |
| required | `True` |

</details>

