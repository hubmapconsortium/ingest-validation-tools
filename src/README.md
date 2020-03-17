# Examples

The interface isn't finalized: For now there is a CLI,
but these examples will use a Python interface, to make testing easier.

```
>>> import cli
>>> cli.print_message('../tests/fixtures/almost-empty/', 'codex-akoya')
This item:
    place-holder.txt
fails this "oneOf" check:
    - $ref: '#/definitions/metadata_csv'
    - properties:
        type:
          enum:
          - directory
This directory:
    place-holder.txt
fails this "contains" check:
    $ref: '#/definitions/metadata_csv'
<BLANKLINE>
1

```
