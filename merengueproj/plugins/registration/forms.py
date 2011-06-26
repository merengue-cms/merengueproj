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

import datetime
import hashlib

from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.utils.importlib import import_module
from django.utils.translation import ugettext, ugettext_lazy as _
from django.template.loader import render_to_string

from merengue.base.forms import BaseModelForm, BaseForm
from merengue.pluggable.utils import get_plugin

from plugins.registration.models import Registration


class RegistrationForm(BaseModelForm):

    username = forms.RegexField(label=_("Username"), max_length=30, regex=r'^[\w.@+-]+$',
        help_text=_("Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only."),
        error_messages={'invalid': _("This value may contain only letters, numbers and @/./+/-/_ characters.")})

    class Meta:
        model = Registration
        exclude = ('registration_hash', )

    def save(self, *args, **kwargs):
        now = datetime.datetime.now()
        instance = self.instance
        instance.registration_date = now
        instance.registration_hash = hashlib.md5('%s-%s-%s' % (instance.username, now, settings.SECRET_KEY)).hexdigest()
        instance = super(RegistrationForm, self).save(*args, **kwargs)
        self.send_email(instance)
        return instance

    def send_email(self, instance):
        domain = Site.objects.get_current().domain
        subject = ugettext(u'Confirm registration at %s') % domain
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = instance.email
        message = render_to_string('registration/register_email.txt', {'domain': domain,
                                                                       'instance': instance})
        send_mail(subject, message, from_email, [to_email])

    def clean_username(self):
        username = self.cleaned_data.get('username', '')
        if not username:
            return username
        if User.objects.filter(username=username).count() or Registration.objects.actives().filter(username=username).count():
            raise forms.ValidationError(_('Username already in use'))
        return username


class RecoverPasswordForm(BaseForm, PasswordResetForm):

    def save(self):
        domain = Site.objects.get_current().domain
        subject = ugettext(u'Password recovery at %s') % domain
        from_email = settings.DEFAULT_FROM_EMAIL
        for user in self.users_cache:
            to_email = self.cleaned_data["email"]
            recovery_hash = hashlib.md5('%s-%s-%s' % (user.username, user.password, settings.SECRET_KEY)).hexdigest()
            message = render_to_string('registration/password_recovery_email.txt', {'domain': domain,
                                                                                    'username': user.username,
                                                                                    'recovery_hash': recovery_hash})
            send_mail(subject, message, from_email, [to_email])


class PasswordForm(BaseForm):

    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"), widget=forms.PasswordInput,
        help_text=_("Enter the same password as above, for verification."))

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1", "")
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError(_("The two password fields didn't match."))
        return password2

    def get_password(self):
        return self.cleaned_data.get('password1')


class DefaultMerengueProfileForm(BaseForm):

    def __init__(self, *args, **kwargs):
        self.registration = kwargs.pop('registration')
        super(DefaultMerengueProfileForm, self).__init__(*args, **kwargs)

    def create_user(self, password):
        user = User(username=self.registration.username,
                    email=self.registration.email)
        user.set_password(password)
        user.save()
        return user

    def save(self, password):
        user = self.create_user(password)
        self.create_profile(user)
        return user

    def create_profile(self, user):
        """ You have to override this function if you want to create an User Profile """
        return None


def get_profile_form():
    plugin_config = get_plugin('registration').get_config()
    form_class_string = plugin_config.get('profile_form_class').get_value()
    if not form_class_string:
        return None
    module_name, class_name = form_class_string.rsplit('.', 1)
    module = import_module(module_name)
    form_class = getattr(module, class_name)
    return form_class
