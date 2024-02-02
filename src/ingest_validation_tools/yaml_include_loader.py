# Not really happy with this. There are approaches that enhance pyyaml
# to add an include syntax...
#   https://gist.github.com/joshbode/569627ced3076931b02f
#   https://pypi.org/project/pyyaml-include/
# but the include happens at a syntactic node,
# so it doesn't help you add elements to a list.
# There is YAML syntax for adding pre-defined keys to a map,
# but there isn't anything analogous for lists.
#
# So, instead, we handle includes as a pre-processing step,
# rather than after the YAML parse.

import re
from pathlib import Path
from typing import Callable

import yaml


def load_yaml(path: Path) -> dict:
    expanded_text = _load_includes(path)
    return yaml.safe_load(expanded_text)


def _load_includes(path: Path, indent: int = 0) -> str:
    text = path.read_text()
    if re.match(r'\s', text[0]):
        raise Exception(f'Unexpected padding in the first column: {path}')
    if re.search(r'\S.*#\s*include:', text):
        raise Exception(f'"# include:" is not alone on a line in: {path}')
    expanded_text = re.sub(
        r'^([ \t]*)#\s*include:\s*(\S+)',
        _expand_match_generator(path.parent),
        text,
        flags=re.MULTILINE
    )
    indent_string = ' ' * indent
    indented_expanded_text = indent_string + re.sub(
        r'^',
        lambda match: indent_string,
        expanded_text,
        flags=re.MULTILINE
    ).strip()
    return indented_expanded_text


def _expand_match_generator(parent_dir: Path) -> Callable:
    def _expand_match(match):
        expanded = _load_includes(
            parent_dir / match.group(2),
            indent=len(match.group(1))
        )
        return expanded
    return _expand_match
