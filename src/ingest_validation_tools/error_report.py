from datetime import datetime
from yaml import Dumper, dump
from webbrowser import open_new_tab
from pathlib import Path
from yattag import Doc, indent


# Force dump not to use alias syntax.
# https://stackoverflow.com/questions/13518819/avoid-references-in-pyyaml
Dumper.ignore_aliases = lambda *args: True


class ErrorReport:
    def __init__(self, errors_dict):
        self.errors = errors_dict

    def _as_list(self):
        return _build_list(self.errors)

    def as_text_list(self):
        return '\n'.join(self._as_list())

    def as_yaml(self):
        return dump(self.errors, sort_keys=False)

    def as_text(self):
        if not self.errors:
            return 'No errors!\n'
        else:
            return self.as_yaml()

    def as_md(self):
        return f'```\n{self.as_text()}```'

    def as_html_fragment(self):
        '''
        >>> print(ErrorReport({}).as_html_fragment())
        No errors!

        >>> report = ErrorReport({'really': 'simple'})
        >>> print(report.as_html_fragment())
        <dl>
          <dt>really</dt>
          <dd>simple</dd>
        </dl>
        '''
        if not self.errors:
            return 'No errors!'
        doc, tag, _, line = Doc().ttl()
        _build_doc(tag, line, self.errors)
        return indent(doc.getvalue())

    def as_html_doc(self):
        doc, tag, text, line = Doc().ttl()
        for_each = "Array.from(document.getElementsByTagName('details')).forEach"
        with tag('html'):
            with tag('head'):
                with tag('style', type='text/css'):
                    text('''
details {
    padding-left: 1em;
}
ul {
    margin: 0;
}''')
            with tag('body'):
                line(
                    'button', 'Open all',
                    onclick=f"{for_each}((node)=>{{node.setAttribute('open','')}})")
                line(
                    'button', 'Close all',
                    onclick=f"{for_each}((node)=>{{node.removeAttribute('open')}})")
                _build_doc(tag, line, self.errors)
        return '<!DOCTYPE html>\n' + indent(doc.getvalue())

    def as_browser(self):
        if not self.errors:
            return self.as_text()
        html = self.as_html_doc()
        filename = f"{str(datetime.now()).replace(' ', '_')}.html"
        path = Path(__file__).parent / 'error-reports' / filename
        path.write_text(html)
        url = f'file://{path.resolve()}'
        open_new_tab(url)
        return f'See {url}'


def _build_list(anything, path=None):
    '''
    >>> flat = _build_list({
    ...     'nested dict': {
    ...         'like': 'this'
    ...     },
    ...     'nested array': [
    ...         'like',
    ...         'this'
    ...     ]
    ... })
    >>> print('\\n'.join(flat))
    nested dict: like: this
    nested array: like
    nested array: this

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
        return [anything]


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
