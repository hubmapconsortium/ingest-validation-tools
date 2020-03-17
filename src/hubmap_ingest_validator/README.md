# Examples

The interface isn't finalized: For now there is a CLI,
but these examples will use a Python interface, to make testing easier.

```
>>> from hubmap_ingest_validator import validator
>>> 1/0
Traceback (most recent call last):
...
ZeroDivisionError: division by zero

>>> validator.validate('../tests/fixtures/almost-empty', 'codex-akoya')
...

```
