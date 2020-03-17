# Examples

The interface isn't finalized: For now there is a CLI,
but these examples will use a Python interface, to make testing easier.

```
>>> import cli
>>> cli.print_message('../tests/fixtures/almost-empty/', 'codex-akoya')
This item:
<BLANKLINE>
    place-holder.txt
<BLANKLINE>
fails this "oneOf" check:
<BLANKLINE>
    - $ref: '#/definitions/metadata_csv'
    - properties:
        type:
          enum:
          - directory
<BLANKLINE>
<BLANKLINE>
<BLANKLINE>
This directory:
<BLANKLINE>
    place-holder.txt
<BLANKLINE>
fails this "contains" check:
<BLANKLINE>
    $ref: '#/definitions/metadata_csv'
<BLANKLINE>
<BLANKLINE>
<BLANKLINE>
1

```
