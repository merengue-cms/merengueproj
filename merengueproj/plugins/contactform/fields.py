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

from django.db import models

from django.forms.util import ValidationError
from django.core.validators import email_re
from django.utils.translation import ugettext as _
from django import forms

from merengue.base import widgets
from merengue.pluggable.utils import get_plugin

from plugins.contactform.utils import captcha_displayajaxhtml

from recaptcha.client import captcha


class RadioField(forms.ChoiceField):
    widget = forms.widgets.RadioSelect


class TextAreaField(forms.CharField):
    widget = forms.widgets.Textarea


class DateTimeField(forms.DateTimeField):
    widget = widgets.SplitDateTimeWidget


class DateField(forms.DateField):
    widget = widgets.InputDateWidget


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


class CaptchaWidget(forms.widgets.Widget):

    def render(self, name, value, attrs=None):
        plugin = get_plugin('contactform')
        pubkey = plugin.get_config().get('rpubk', None)
        if pubkey:
            pubkey = pubkey.value
        else:
            pubkey = ''
        return captcha.displayhtml(pubkey)

    def value_from_datadict(self, data, files, name):
        return (data['recaptcha_challenge_field'],
                data['recaptcha_response_field'])


class CaptchaField(forms.Field):
    widget = CaptchaWidget

    def __init__(self, client_addr, *args, **kwargs):
        self.client_addr = client_addr
        super(CaptchaField, self).__init__(*args, **kwargs)

    def clean(self, value):
        plugin = get_plugin('contactform')
        privkey = plugin.get_config().get('rprivk', None)
        if privkey:
            privkey = privkey.value
        else:
            privkey = ''
        challenge, response = value
        recaptcha_response = captcha.submit(challenge, response,
                                            privkey, self.client_addr)
        if not recaptcha_response.is_valid:
            raise ValidationError(_("The captcha was invalid, try again."))


class CaptchaAjaxWidget(CaptchaWidget):

    def render(self, name, value, attrs=None):
        plugin = get_plugin('contactform')
        pubkey = plugin.get_config().get('rpubk', None)
        if pubkey:
            pubkey = pubkey.value
        else:
            pubkey = ''
        return captcha_displayajaxhtml(pubkey)


class CaptchaAjaxField(CaptchaField):
    widget = CaptchaAjaxWidget
