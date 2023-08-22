from __future__ import annotations

from re import sub
from typing import Union

pat_reps = [
    (r'constraint "pattern" is (".*")', "it does not match the expected pattern"),
    (r"^Metadata TSV Errors: \S+/", "In "),
    (
        r".*: External: (row \d+), data ([^:]+): ([^:]+): (.+)",
        r'In the dataset \2 referenced on \1, the file "\4" is \3.',
        # TODO: updating patterns
        # r"(row \d+), field ([^:]+): '([^:]+): (.+)'",
        # r'In the field \2 referenced on \1, the file "\4" \3.',
    ),
    (
        # TODO: outdated
        r" \(as \S+\): External: Warning: File has no data rows",
        r", the file is just a header with no data rows",
    ),
    (
        r"Reference Errors: Multiple References: (\S+): .*/(.*)",
        r'The dataset directory "\1" is referenced by \2, '
        r"and somewhere else, but references should be unique.",
    ),
    (
        r"Reference Errors: No References: Directories: ",
        "At the root of an upload, the only directories should be datasets. No TSV references ",
    ),
    (
        r"Reference Errors: No References: Files: ",
        "At the root of an upload, the only files should be TSVs. No TSV references ",
    ),
    (r"Metadata TSV Errors: Missing: ", ""),
    (r'is not type "(\w+)" and format "default"', r"is not a \1"),
    (r"(,|is) [A-Z]", lambda match: match.group(0).lower()),
    (r'constraint "enum" is "\[(.*)\]"', r"it is not one of these: \1"),
    (r"is no such file or directory", r"does not exist"),
    (
        r'the file "([^"]+)" is required but missing',
        r'a file matching "\1" is required but missing',
    ),
    # Quick and dirty fix to stop message munger from adding period following ints,
    # because that messes with CEDAR validation report
    (r"([^.\d])$", r"\1."),
    (r'type is "datetime/.*"', r"it is not in the format YYYY-MM-DD Hour:Minute"),
    (r'type is "boolean/default"', r"it is neither true nor false"),
    (r'type is "number/default"', r"it is not in numerical form"),
    (r'type is "integer/default"', r"it is not an integer"),
    (r'URL returned .* "https://dx.doi.org/.*"', r"it is an invalid DOI"),
    (
        r'(a file matching ".*" is required but missing.)',
        r"\1 Please review the schema for more information.",
    ),
    (r"\'", '"'),
    (r'type is "string/email"', r"it is not a valid email"),
    (r'constraint "required" .*', r"it must be filled out."),
]


def munge(message: Union[str, int]) -> Union[str, int]:
    """
    Make the error message less informative.

    >>> munge('In md.tsv (as fake): External: row 2, data fake/ds: Not allowed: nope.txt')
    'In the dataset fake/ds referenced on row 2, the file "nope.txt" is not allowed.'

    """
    for pattern, replacement in pat_reps:
        if type(message) == int:
            message = int(sub(pattern, replacement, str(message)))
        else:
            message = sub(pattern, replacement, message)
    return message


def recursive_munge(message_collection):
    if isinstance(message_collection, dict):
        return {k: recursive_munge(v) for k, v in message_collection.items()}
    elif isinstance(message_collection, list):
        return [recursive_munge(v) for v in message_collection]
    else:
        return munge(message_collection)
