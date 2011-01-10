# Copyright (c) 2010 by Yaco Sistemas
#
# This file is part of Merengue.
#
# Merengue is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Merengue is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Merengue.  If not, see <http://www.gnu.org/licenses/>.

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
            error_message = getattr(e, 'msg', e.message)
            raise ValidationError(_('Syntax Error %s' % error_message.replace('\\n', '').replace('\\r', '')))
        if self.request.POST.get('%s_normalize' % self.name, None):
            clean_value = value_parse.cssText
        if self.request.POST.get('%s_show_all_errors' % self.name, None):
            errors_and_warning = mylog.getvalue()
            if errors_and_warning:
                raise ValidationError(errors_and_warning)
        return clean_value
