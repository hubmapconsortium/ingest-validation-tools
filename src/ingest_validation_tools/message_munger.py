from re import sub


def munge(message):
    '''
    Make the error message less informative.
    '''
    pat_reps = [
        (r'does not conform to the pattern constraint of .*',
         'is not the right form.'),

        (r'^Metadata TSV Errors: \S+/',
         'In '),

        (r' \(as \S+\): Internal:',
         ','),

        (r'.*: External: ([^:]+): ([^:]+): (.+)',
         r'In the dataset referenced by \1, the file "\3" is \2.'),

        (r' \(as \S+\): External: Warning: File has no data rows',
         r', the file is just a header with no data rows'),

        (r'Reference Errors: Multiple References: (\S+): .*/(.*)',
         r'The dataset directory "\1" is referenced by \2, '
         r'and somewhere else, but references should be unique.'),

        (r'Reference Errors: No References: ',
         'There are no references from any TSV to '),

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
