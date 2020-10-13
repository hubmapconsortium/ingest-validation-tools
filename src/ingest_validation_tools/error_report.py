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
        >>> report = ErrorReport({'really': 'simple'})
        >>> print(report.as_html_fragment())
        <dl>
          <dt>really</dt>
          <dd>simple</dd>
        </dl>
        '''
        doc, tag, _, line = Doc().ttl()
        _build_doc(tag, line, self.errors)
        return indent(doc.getvalue())

    def as_html_doc(self):
        '''
        >>> report = ErrorReport({'really': 'simple'})
        >>> print(report.as_html_doc())
        <html>
          <body>
            <dl>
              <dt>really</dt>
              <dd>simple</dd>
            </dl>
          </body>
        </html>
        '''
        doc, tag, text, line = Doc().ttl()
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
