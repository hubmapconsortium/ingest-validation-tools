from __future__ import annotations

from re import sub
from typing import Union

# TODO: are the patterns that rely on specific keys even being used?
# The message does not include keys.
pat_reps = [
    (r'constraint "pattern" is (".*")', "it does not match the expected pattern"),
    (r"^Metadata TSV Errors: \S+/", "In "),
    (
        r"^.*Directory Errors: (\S*) \(as \S*\): (row \d+), field (\S*): (.*): (.*)",
        r'In the dataset \1, in field \3 referenced on \2, the file "\5" is \4.',
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
    # TODO: this actually makes a lot of stuff worse, is it better to remove?
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
    (r"\<.*?\>", ""),
    (
        r"400 Client Error: Bad Request for url: (.*).",
        r"Field value is not valid; URL \1 returned a 400 Error.",
    ),
]


def munge(message: Union[str, int]) -> Union[str, int]:
    """
    Make the error message less informative.

    >>> munge('Directory Errors: examples/dataset/fake (as fake): row 2, field fake_path: Not allowed: nope.txt')  # noqa E501
    'In the dataset examples/dataset/fake, in field fake_path referenced on row 2, the file "nope.txt" is not allowed.'

    """
    for pattern, replacement in pat_reps:
        if message is None:
            message = ""
        elif isinstance(message, int):
            message = int(sub(pattern, replacement, str(message)))
        else:
            message = sub(pattern, replacement, str(message))
    return message


def recursive_munge(message_collection):
    if isinstance(message_collection, dict):
        return {k: recursive_munge(v) for k, v in message_collection.items()}
    elif isinstance(message_collection, list):
        return [recursive_munge(v) for v in message_collection]
    else:
        return munge(message_collection)
