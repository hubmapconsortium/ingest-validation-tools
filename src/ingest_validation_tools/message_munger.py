from re import sub


def munge(message):
    '''
    Make the error message less informative.
    '''
    pat_reps = [
        (r'does not conform to the pattern constraint of .*',
        'is not the right pattern.'),
        
        (r'^Metadata TSV Errors: \S+/',
        'In '),
        
        (r' \(as \S+\): Internal:',
        ','),

        (r'.*: External: ([^:]+): ([^:]+): (.+)',
        r'In \1, the file "\3" is \2.'),

        (r'Reference Errors: Multiple References: (\S+): .*/(.*)',
        r'The dataset directory "\1" is referenced by \2, and somewhere else; References should be unique.')
    ]
    for pattern, replacement in pat_reps:
        message = sub(pattern, replacement, message)
    return message
