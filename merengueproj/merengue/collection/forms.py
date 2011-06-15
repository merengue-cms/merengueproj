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
from django.contrib.contenttypes.models import ContentType
from django.utils.importlib import import_module

from merengue.base.forms import BaseAdminModelForm


class CollectionFilterForm(forms.ModelForm):
    """
    Collection form provides validation.
    """

    ISNULL_VALID_CHOICES = ('true', 'false', )

    def clean(self):
        cdata = self.cleaned_data
        if cdata.get('filter_operator') == 'isnull' and \
            cdata.get('filter_value') not in self.ISNULL_VALID_CHOICES:
            raise forms.ValidationError("Value should be 'true' or 'false'")
        if not self.instance:
            return self.cleaned_data
        collection = cdata.get('collection', None)
        if not collection:
            return self.cleaned_data
        if collection.pk:
            content_types = collection.content_types.all()
        else:
            content_types = ContentType.objects.filter(id__in=self.data.getlist('content_types'))
        if not content_types:
            return self.cleaned_data
        try:
            model = content_types[0].model_class()
            query = model.objects.all()
            self.instance.filter_field = cdata.get('filter_field')
            self.instance.filter_operator = cdata.get('filter_operator')
            self.instance.filter_value = cdata.get('filter_value')
            self.instance.filter_query(query).count()
        except Exception, e:
            # Close connection if it brokes
            from django.db import connection
            connection.close()
            raise forms.ValidationError(e)
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


class CollectionAdminModelForm(BaseAdminModelForm):

    def __init__(self, *args, **kwargs):
        super(CollectionAdminModelForm, self).__init__(*args, **kwargs)
        if 'content_types' in self.fields:
            self.fields['content_types'].required = True
