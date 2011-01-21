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
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.utils.importlib import import_module

from autoreports.forms import FormAdminDjango

from merengue.base.forms import BaseAdminModelForm
from merengue.block.models import RegisteredBlock
from merengue.registry.fields import ConfigFormField
from merengue.registry.params import ConfigDict


class BaseContentRelatedBlockForm(BaseAdminModelForm):

    def __init__(self, *args, **kwargs):
        super(BaseContentRelatedBlockForm, self).__init__(*args, **kwargs)
        if args:
            block_id = args[0]['block']
            reg_block = RegisteredBlock.objects.get(id=block_id)
        else:
            try:
                reg_block = self.instance.block
            except ObjectDoesNotExist:
                reg_block = None
        if reg_block:
            block = getattr(import_module(reg_block.module),
                            reg_block.class_name)
            self.fields['config'].set_config(ConfigDict(block.config_params,
                                                        self.instance.config))

    class Media:
        js = (
            settings.MEDIA_URL + 'merengue/js/block/dynamic-config-param.js',
            )


class BlockConfigForm(forms.Form, FormAdminDjango):

    config = ConfigFormField()
