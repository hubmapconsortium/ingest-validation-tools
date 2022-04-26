from re import sub


def munge(message: str) -> str:
    '''
    Make the error message less informative.

    >>> munge('In md.tsv (as fake): External: row 2, data fake/ds: Not allowed: nope.txt')
    'In the dataset fake/ds referenced on row 2, the file "nope.txt" is not allowed.'

    '''
    pat_reps = [
        (r'does not conform to the pattern constraint of .*',
         'is not the right form.'),

        (r'^Metadata TSV Errors: \S+/',
         'In '),

        (r'.*: External: (row \d+), data ([^:]+): ([^:]+): (.+)',
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

        (r'does not conform to the given enumeration: "\[(.*)\]"',
         r'is not one of these: \1'),

        (r'is no such file or directory',
         r'does not exist'),

        (r'the file "([^"]+)" is required but missing',
         r'a file matching "\1" is required but missing'),

        (r'([^.])$',
         r'\1.')
    ]
    for pattern, replacement in pat_reps:
        message = sub(pattern, replacement, message)
    return message
