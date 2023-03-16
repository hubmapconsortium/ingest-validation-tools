from re import sub

pat_reps = [
    (r'constraint "pattern" is (".*")',
     'it does not match the expected pattern'),

    (r'^Metadata TSV Errors: \S+/',
     'In '),

    (r'(row \d+), data ([^:]+): ([^:]+): (.+)',
     r'In the dataset \2 referenced on \1, the file "\4" is \3.'),

    (r' \(as \S+\): External: Warning: File has no data rows',
     r', the file is just a header with no data rows'),

    (r'Reference Errors: Multiple References: (\S+): .*/(.*)',
     r'The dataset directory "\1" is referenced by \2, '
     r'and somewhere else, but references should be unique.'),

    (r'Reference Errors: No References: Directories: ',
     'At the root of an upload, the only directories should be datasets. No TSV references '),
    (r'Reference Errors: No References: Files: ',
     'At the root of an upload, the only files should be TSVs. No TSV references '),

    (r'Metadata TSV Errors: Missing: ',
     ''),

    (r'is not type "integer" and format "default"',
     r'is not an integer'),

    (r'is not type "(\w+)" and format "default"',
     r'is not a \1'),

    (r'(,|is) [A-Z]',
     lambda match: match.group(0).lower()),

    (r'constraint "enum" is "\[(.*)\]"',
     r'it is not one of these: \1'),

# 'On row 2, column "acquisition_instrument_vendor", value "acquisition_instrument_vendor" fails because constraint "enum" is "[\'Keyence\', \'Zeiss\']"'

    (r'is no such file or directory',
     r'does not exist'),

    (r'the file "([^"]+)" is required but missing',
     r'a file matching "\1" is required but missing'),

    (r'([^.])$',
     r'\1.'),

    (r'type is "datetime/.*"',
     r'it is not in the format YYYY-MM-DD Hour:Minute'),

    (r'type is "boolean/default"',
     r'it is neither true nor false'),

    (r'type is "number/default"',
     r'it is not in numerical form'),

    (r'type is "integer/default"',
     r'it is not an integer'),

    (r'URL returned .* "https://dx.doi.org/.*"',
     r'it is an invalid DOI'),

    (r'(a file matching ".*" is required but missing.)',
     r'\1 Please review the schema for more information.'),

    (r'\'',
     '\"'),

    (r'type is "string/email"',
     r'it is not a valid email'),

    (r'constraint "required" .*',
     r'it must be filled out.'),
]

def munge(message: str) -> str:
    '''
    Make the error message less informative.

    >>> munge('In md.tsv (as fake): External: row 2, data fake/ds: Not allowed: nope.txt')
    'In the dataset fake/ds referenced on row 2, the file "nope.txt" is not allowed.'

    '''
    for pattern, replacement in pat_reps:
        message = sub(pattern, replacement, message)
    return message


def recursive_munge(message_collection):
    if isinstance(message_collection, dict):
        if all(isinstance(v, (float, int, str)) for v in message_collection.values()):
            return [munge(v) for v in message_collection.values()]
        else:
            for k, v in message_collection.items():
                message_collection[k] = recursive_munge(v)
            return message_collection
    elif isinstance(message_collection, list):
        if all(isinstance(v, (float, int, str)) for v in message_collection):
            return [munge(v) for v in message_collection]
        else:
            to_return = []
            for v in message_collection:
                to_return += recursive_munge(v)
            return to_return
    else:
        return munge(message_collection)
