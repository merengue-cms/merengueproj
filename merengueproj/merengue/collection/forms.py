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

from django import forms
from django.utils.importlib import import_module


class CollectionFilterForm(forms.ModelForm):
    """
    Collection form provides validation.
    """

    ISNULL_VALID_CHOICES = ('true', 'false', )

    def clean(self):
#        @FIXME: Hardcoded string
        cdata = self.cleaned_data
        if cdata.get('filter_operator') == 'isnull' and \
            cdata.get('filter_value') not in self.ISNULL_VALID_CHOICES:
            raise forms.ValidationError("Value should be 'true' or 'false'")

        return self.cleaned_data


class CollectionDisplayFilterForm(forms.ModelForm):

    def clean(self):
        module = self.cleaned_data.get('filter_module')
        params = self.cleaned_data.get('filter_params')
        if not module or not params:
            return self.cleaned_data
        filter_module_name, filter_module_function = module.rsplit('.', 1)
        func = getattr(import_module(filter_module_name), filter_module_function, None)
        value = ''
        if params:
            params = params.split(',')
            try:
                value = func(value, *params)
            except Exception, e:
                raise forms.ValidationError(e)
        return self.cleaned_data
