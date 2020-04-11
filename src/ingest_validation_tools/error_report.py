from yaml import dump


class ErrorReport:
    def __init__(self, errors_dict):
        self.errors = errors_dict

    def as_yaml(self):
        return dump(self.errors, sort_keys=False)

    def as_html_fragment(self):
        return f'<pre>{self.as_yaml()}</pre>'

    def as_html_document(self):
        return f'<html><body>{self.as_html_fragment()}</body></html>'

    def as_text(self):
        if not self.errors:
            return 'No errors!'
        else:
            return self.as_yaml()
