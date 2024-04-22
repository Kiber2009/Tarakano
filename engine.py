from wtforms.validators import ValidationError


class SymbolsAnyOf:
    def __init__(self, values, message=None, values_formatter=None):
        self.values = values
        self.message = message
        if values_formatter is None:
            values_formatter = self.default_values_formatter
        self.values_formatter = values_formatter

    def __call__(self, form, field):
        t = True
        for i in field.data:
            if i not in self.values:
                t = False
                break
        if t:
            return

        message = self.message
        if message is None:
            message = field.gettext("Invalid value, must be one of: %(values)s.")

        raise ValidationError(message % dict(values=self.values_formatter(self.values)))

    @staticmethod
    def default_values_formatter(values):
        return ", ".join(str(x) for x in values)


def cut_str(text, length):
    if len(text) <= length:
        return text
    return text[:length] + ' ...'
