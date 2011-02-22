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
from django.utils.translation import ugettext_lazy as _

from autoreports.forms import FormAdminDjango

from merengue.base.forms import BaseAdminModelForm
from merengue.pluggable.models import RegisteredPlugin
from merengue.registry import register
from merengue.registry.fields import ConfigFormField


class BaseContentRelatedBlockAddForm(forms.Form):
    block_class = forms.ChoiceField(
        label=_('Block to add'),
    )

    def __init__(self, *args, **kwargs):
        super(BaseContentRelatedBlockAddForm, self).__init__(*args, **kwargs)
        active_plugins = RegisteredPlugin.objects.actives().get_items()
        blocks_classes = []
        for plugin in active_plugins:
            blocks_classes.extend(plugin.get_blocks())
        self.fields['block_class'].choices = [
            ('%s.%s' % (b.get_module(), b.get_class_name()), b.name) for b in blocks_classes
        ]

    def save(self, *args, **kwargs):
        block_class_path = self.cleaned_data['block_class']
        class_name = block_class_path.split('.')[-1]
        module_path = '.'.join(block_class_path.split('.')[:-1])
        module = import_module(module_path)
        block_class = getattr(module, class_name)
        reg_block = register(block_class)
        reg_block.active = True
        reg_block.content = self.cleaned_data['content']
        reg_block.save()
        return reg_block

    def save_m2m(self, *args, **kwargs):
        pass


class BaseContentRelatedBlockChangeForm(BaseAdminModelForm):
    pass


class BlockConfigForm(forms.Form, FormAdminDjango):

    config = ConfigFormField()
