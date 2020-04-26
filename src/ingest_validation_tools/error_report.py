from datetime import datetime
from yaml import Dumper, dump
from webbrowser import open_new_tab
from pathlib import Path
from html import escape


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
        return f'<pre>\n{self.as_text()}</pre>'

    def as_html(self):
        escaped = escape(self.as_text())
        return f'<html><body><pre>{escaped}</pre></body></html>'

    def as_browser(self):
        if not self.errors:
            return self.as_text()
        html = self.as_html()
        filename = f"{str(datetime.now()).replace(' ', '_')}.html"
        path = Path(__file__).parent / 'error-reports' / filename
        path.write_text(html)
        url = f'file://{path.resolve()}'
        open_new_tab(url)
        return f'See {url}'
