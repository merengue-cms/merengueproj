import logging
import cssutils
import StringIO

from xml.dom import SyntaxErr
from django.forms import fields
from django.forms.util import ValidationError
from django.utils.translation import ugettext_lazy as _

from merengue.section.widgets import CSSValidatorWidget


class CSSValidatorField(fields.CharField):

    widget = CSSValidatorWidget

    def __init__(self, name, request, *args, **kwargs):
        super(CSSValidatorField, self).__init__(*args, **kwargs)
        self.request = request
        self.name = name

    def clean(self, value):
        clean_value = super(CSSValidatorField, self).clean(value)
        mylog = StringIO.StringIO()
        h = logging.StreamHandler(mylog)
        h.setFormatter(logging.Formatter('%(levelname)s %(message)s'))
        cssutils.log.addHandler(h)
        cssutils.log.setLevel(logging.INFO)
        parser = cssutils.CSSParser(raiseExceptions=True)
        try:
            value_parse = parser.parseString(clean_value)
        except SyntaxErr, e:
            raise ValidationError(_('Syntax Error %s' % e.msg.replace('\\n', '').replace('\\r', '')))
        if self.request.POST.get('%s_normalize' % self.name, None):
            clean_value = value_parse.cssText
        if self.request.POST.get('%s_show_all_errors' % self.name, None):
            errors_and_warning = mylog.getvalue()
            if errors_and_warning:
                raise ValidationError(errors_and_warning)
        return clean_value
