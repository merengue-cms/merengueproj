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

from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserChangeForm as DjangoUserChangeForm
from django.contrib.auth.models import User
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils import formats
from django.utils.translation import ugettext_lazy as _

from merengue.base.models import BaseContent
from merengue.perms import ANONYMOUS_ROLE_SLUG
from merengue.perms.models import Role, PrincipalRoleRelation, Permission, AccessRequest
from merengue.perms.utils import get_global_roles, add_local_role, get_roles

from ajax_select.fields import AutoCompleteSelectField


class UserChangeForm(DjangoUserChangeForm):

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        user = kwargs.get('instance', None)
        if user:
            self.fields['roles'].initial = [role.id for role in get_global_roles(user)]

    roles = forms.ModelMultipleChoiceField(queryset=Role.objects.exclude(name=u'Anonymous User'),
                                           widget=FilteredSelectMultiple(_('Roles'), False),
                                           required=False)


class GroupForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)
        group = kwargs.get('instance', None)
        if group:
            self.fields['roles'].initial = [role.id for role in get_global_roles(group)]


class PrincipalRoleRelationForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(PrincipalRoleRelationForm, self).__init__(*args, **kwargs)
        self.fields['content'].widget = forms.HiddenInput()
        self.fields['user'] = AutoCompleteSelectField('perms_user', required=False)
        self.fields['group'] = AutoCompleteSelectField('perms_group', required=False)
        self.fields['role'].queryset = self.fields['role'].queryset.exclude(slug=ANONYMOUS_ROLE_SLUG)

    class Meta:
        model = PrincipalRoleRelation

    class Media:
        css = {'all': ('merengue/css/ajaxautocompletion/jquery.autocomplete.css',
                       'merengue/css/ajax_select/iconic.css')}

        js = ('merengue/js/ajaxautocompletion/jquery.autocomplete.js',
              'merengue/js/ajax_select/ajax_select.js')

    def save(self):
        obj = self.cleaned_data['content']
        principal = self.cleaned_data.get('user') or self.cleaned_data.get('group', None)
        role = self.cleaned_data['role']
        #import ipdb; ipdb.set_trace()
        add_local_role(obj, principal, role)

    def clean(self):
        cleaned_data = self.cleaned_data
        user = cleaned_data.get("user")
        group = cleaned_data.get("group")

        if not user and not group:
            raise forms.ValidationError("User and group fields are empty, you must enter or user or group")
        return cleaned_data


class AccessRequestForm(forms.ModelForm):

    def __init__(self, request, exception, *args, **kwargs):
        super(AccessRequestForm, self).__init__(*args, **kwargs)
        self.user = request.user.is_authenticated() and request.user or None
        if exception:
            self.fields['url'].initial = request.get_full_path()
            self.fields['access_time'].initial = datetime.datetime.now().strftime(formats.get_format('DATETIME_INPUT_FORMATS')[0])
            content = getattr(exception, 'content', None)
            if content and isinstance(content, BaseContent):
                self.fields['content'].initial = content
            perm = getattr(exception, 'perm', None)
            if perm:
                self.fields['permission'].initial = Permission.objects.get(codename=perm)
        self.fields['url'].widget = forms.HiddenInput()
        self.fields['permission'].widget = forms.HiddenInput()
        self.fields['access_time'].widget = forms.HiddenInput()
        self.fields['content'].widget = forms.HiddenInput()

    def get_owners_of_content(self, obj):
        content = obj.content
        if not content:
            return None
        owners_content = content.get_owners()
        owner_filter = Q(id__in=owners_content.values('id').query)
        sections = content.sections.all()
        for section in sections:
            owners_section = section.get_owners()
            owner_filter = owner_filter | Q(id__in=owners_section.values('id').query)
        return User.objects.filter(owner_filter).filter(email__isnull=False).exclude(email='')

    def notification_access_request(self, obj, owners):
        owners = owners or User.objects.filter(is_superuser=True)
        subject = _(u'You have a access request')
        from_email = settings.EMAIL_HOST_USER
        to_email = [user.email for user in owners]
        site = Site.objects.get_current()
        domain = 'http://%s' % site.domain
        text_content = render_to_string('perms/email_access_request.html', {'obj': obj, 'domain': domain, 'tags': False})
        html_content = render_to_string('perms/email_access_request.html', {'obj': obj, 'domain': domain, 'tags': True})
        msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        msg.attach_alternative(html_content, "text/html")
        msg.send()

    def save(self, *args, **kwargs):
        obj = super(AccessRequestForm, self).save(*args, **kwargs)
        obj.state = obj.content.workflow_status
        if self.user:
            obj.user = self.user
            roles = get_roles(obj.user, obj.content)
            for rol in roles:
                obj.roles.add(rol)
        obj.roles.add(Role.objects.get(slug=ANONYMOUS_ROLE_SLUG))
        owners = self.get_owners_of_content(obj)
        for owner in owners:
            obj.owners.add(owner)
        obj.save()
        self.notification_access_request(obj, owners)
        return obj

    class Meta:
        model = AccessRequest
        exclude = ('state', 'roles', 'is_done', 'owners', 'user')
