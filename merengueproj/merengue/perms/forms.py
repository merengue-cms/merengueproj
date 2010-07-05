# Copyright (c) 2010 by Yaco Sistemas <msaelices@yaco.es>
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

from django import forms
from django.contrib.auth.forms import UserChangeForm as DjangoUserChangeForm

from django.utils.translation import ugettext_lazy as _

from django.contrib.admin.widgets import FilteredSelectMultiple
from merengue.perms import ANONYMOUS_ROLE_SLUG
from merengue.perms.models import Role, PrincipalRoleRelation
from merengue.perms.utils import get_global_roles, add_local_role

from ajax_select.fields import AutoCompleteSelectField


class UserChangeForm(DjangoUserChangeForm):

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        user = kwargs.get('instance', None)
        if user:
            self.fields['roles'].initial = [role.id for role in get_global_roles(user)]

    roles = forms.ModelMultipleChoiceField(queryset=Role.objects.all(),
                                           widget=FilteredSelectMultiple(_('Roles'), False),
                                           required=False)


class GroupForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)
        group = kwargs.get('instance', None)
        if group:
            self.fields['roles'].initial = [role.id for role in get_global_roles(group)]

    roles = forms.ModelMultipleChoiceField(queryset=Role.objects.all(),
                                          widget=FilteredSelectMultiple(_('Roles'), False),
                                          required=False)


class PrincipalRoleRelationForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(PrincipalRoleRelationForm, self).__init__(*args, **kwargs)
        self.fields['content'].widget = forms.HiddenInput()
        self.fields['user'] = AutoCompleteSelectField('perms_user')
        self.fields['role'].queryset = self.fields['role'].queryset.exclude(slug=ANONYMOUS_ROLE_SLUG)

        del self.fields['group']

    class Meta:
        model = PrincipalRoleRelation

    class Media:
        css = {'all': ('merengue/css/ajaxautocompletion/jquery.autocomplete.css',
                       'merengue/css/ajax_select/iconic.css')}

        js = ('merengue/js/ajaxautocompletion/jquery.autocomplete.js',
              'merengue/js/ajax_select/ajax_select.js')

    def save(self):
        obj = self.cleaned_data['content']
        prinpipal = self.cleaned_data.get('user', self.cleaned_data.get('group', None))
        role = self.cleaned_data['role']
        add_local_role(obj, prinpipal, role)
