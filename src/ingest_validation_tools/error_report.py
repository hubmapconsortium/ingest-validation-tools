from datetime import datetime
from yaml import Dumper, dump
from webbrowser import open_new_tab
from pathlib import Path
from typing import List

from ingest_validation_tools.message_munger import munge


# Force dump not to use alias syntax.
# https://stackoverflow.com/questions/13518819/avoid-references-in-pyyaml
Dumper.ignore_aliases = lambda *args: True


class ErrorReport:
    def __init__(self, errors_dict, effective_tsv_paths={}):
        self.errors = errors_dict
        self.effective_tsv_paths = effective_tsv_paths
        if self.errors:
            self.errors['Hint'] = \
                'If validation fails because of extra whitespace in the TSV, try:\n' \
                'src/cleanup_whitespace.py --tsv_in original.tsv --tsv_out clean.tsv'

    def _no_errors(self):
        schema_versions = ' and '.join(
            f'{sv.schema_name}-v{sv.version} ({Path(path).name})'
            for path, sv in self.effective_tsv_paths.items()
        )
        return f'No errors! {schema_versions}\n'

    def _as_list(self) -> List[str]:
        return [munge(m) for m in _build_list(self.errors)]

    def as_text_list(self) -> str:
        return '\n'.join(self._as_list()) or self._no_errors()

    def as_yaml(self) -> str:
        return dump(self.errors, sort_keys=False)

    def as_text(self) -> str:
        if not self.errors:
            return self._no_errors()
        else:
            return self.as_yaml()

    def as_md(self) -> str:
        return f'```\n{self.as_text()}```'


def _build_list(anything, path=None) -> List[str]:
    '''
    >>> flat = _build_list({
    ...     'nested dict': {
    ...         'like': 'this'
    ...     },
    ...     'nested array': [
    ...         'like',
    ...         'this'
    ...     ],
    ...     'string': 'like this',
    ...     'number': 42
    ... })
    >>> print('\\n'.join(flat))
    nested dict: like: this
    nested array: like
    nested array: this
    string: like this
    number: 42

    '''
    prefix = f'{path}: ' if path else ''
    if isinstance(anything, dict):
        if all(isinstance(v, (float, int, str)) for v in anything.values()):
            return [f'{prefix}{k}: {v}' for k, v in anything.items()]
        else:
            to_return = []
            for k, v in anything.items():
                to_return += _build_list(v, path=f'{prefix}{k}')
            return to_return
    elif isinstance(anything, list):
        if all(isinstance(v, (float, int, str)) for v in anything):
            return [f'{prefix}{v}' for v in anything]
        else:
            to_return = []
            for v in anything:
                to_return += _build_list(v, path=path)
            return to_return
    else:
        return [f'{prefix}{anything}']


def _build_doc(tag, line, anything):
    '''
    >>> doc, tag, text, line = Doc().ttl()
    >>> _build_doc(tag, line, {
    ...     'nested dict': {
    ...         'like': 'this'
    ...     },
    ...     'nested array': [
    ...         'like',
    ...         'this'
    ...     ]
    ... })
    >>> print(indent(doc.getvalue()))
    <details>
      <summary>nested dict</summary>
      <dl>
        <dt>like</dt>
        <dd>this</dd>
      </dl>
    </details>
    <details>
      <summary>nested array</summary>
      <ul>
        <li>like</li>
        <li>this</li>
      </ul>
    </details>

    '''
    if isinstance(anything, dict):
        if all(isinstance(v, (float, int, str)) for v in anything.values()):
            with tag('dl'):
                for k, v in anything.items():
                    line('dt', k)
                    line('dd', v)
        else:
            for k, v in anything.items():
                with tag('details'):
                    line('summary', k)
                    _build_doc(tag, line, v)
    elif isinstance(anything, list):
        if all(isinstance(v, (float, int, str)) for v in anything):
            with tag('ul'):
                for v in anything:
                    line('li', v)
        else:
            for v in anything:
                _build_doc(tag, line, v)
    else:
        line('div', anything)
