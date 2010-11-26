# Copyright (c) 2010 by Yaco Sistemas <dgarcia@yaco.es>
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


from django.conf import settings

if settings.USE_GIS:
    from django.contrib.gis.db import models
else:
    from django.db import models

from django.contrib.admin import widgets
from django.forms.util import ValidationError
from django.forms.fields import email_re
from django.utils.translation import ugettext as _
from django import forms


class TextAreaField(forms.CharField):
    widget = forms.widgets.Textarea


class DateTimeField(forms.DateTimeField):
    widget = widgets.AdminSplitDateTime


class DateField(forms.DateField):
    widget = widgets.AdminDateWidget


class MultiEmailField(forms.CharField):
    widget = forms.widgets.Textarea

    def clean(self, value):
        super(MultiEmailField, self).clean(value)
        if value:
            emails = map(unicode.strip, value.split(','))
        else:
            return value

        for email in emails:
            if not email_re.match(email):
                raise ValidationError(_("This is not a valid comma separated email list."))

        return value


class ModelMultiEmailField(models.TextField):

    def formfield(self, **kwargs):
        defaults = {'form_class': MultiEmailField}
        defaults.update(kwargs)
        return super(ModelMultiEmailField, self).formfield(**defaults)
