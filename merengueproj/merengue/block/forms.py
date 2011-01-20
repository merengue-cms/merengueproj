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
from django.conf import settings

from autoreports.forms import FormAdminDjango
#from cmsutils.forms.fields import JSONFormField

from merengue.base.forms import BaseAdminModelForm
from merengue.registry.fields import ConfigFormField
from merengue.registry.widgets import ConfigWidget


class BaseContentRelatedBlockForm(BaseAdminModelForm):

    def __init__(self, *args, **kwargs):
        super(BaseContentRelatedBlockForm, self).__init__(*args, **kwargs)
        self.fields['config'].widget = ConfigWidget()

    class Media:
        js = (
            settings.MEDIA_URL + 'merengue/js/block/dynamic-config-param.js',
            )


class BlockConfigForm(forms.Form, FormAdminDjango):

    config = ConfigFormField()
