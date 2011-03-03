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
from django.db.models import Q
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

        # set to not rewrite if content has already a block of this kind
        filters = {'module': module_path, 'class_name': class_name,
                   'placed_at': getattr(block_class, 'default_place', None)}
        if reg_block.content.registeredblock_set.filter(**filters).count():
            reg_block.overwrite_if_place = False

        reg_block.save()
        return reg_block

    def save_m2m(self, *args, **kwargs):
        pass


class BaseContentRelatedBlockChangeForm(BaseAdminModelForm):

    def clean(self, *args, **kwargs):
        """
        check if the block is going to be overwritten by another block within the same content
        see discussion @ https://dev.merengueproject.org/ticket/1575#comment:6
        """
        self.cleaned_data = super(BaseContentRelatedBlockChangeForm, self).clean(*args, **kwargs)
        content = self.instance.content
        overwrite_if_place = self.cleaned_data['overwrite_if_place']
        overwrite_always = self.cleaned_data['overwrite_always']
        if self.cleaned_data['overwrite_if_place'] or self.cleaned_data['overwrite_always']:
            same_block_filters = {'module': self.instance.module, 'class_name': self.instance.class_name}
            has_placed = content.registeredblock_set.filter(~Q(id=self.instance.id),
                                                            overwrite_if_place=True,
                                                            placed_at=self.cleaned_data['placed_at'],
                                                            **same_block_filters).count()
            has_generic = content.registeredblock_set.filter(~Q(id=self.instance.id),
                                                            overwrite_always=True,
                                                            **same_block_filters).count()
            place_error = _("Placing the block here will take no effect, as another related block is set to overwrite it")
            place_overwrite_error = _("Unmark this field to keep the block in the specified place\
                                       (even though it won't be displayed)")
            noeffect_error = _("A block is already set to overwrite others of this kind.\
                                Unmark this to save the block, even though it won't be displayed")
            if has_generic and overwrite_if_place:
                self._errors['overwrite_if_place'] = self.error_class([noeffect_error])
            elif has_generic and overwrite_always:
                self._errors['overwrite_always'] = self.error_class([noeffect_error])
            elif has_placed and overwrite_if_place:
                self._errors['overwrite_if_place'] = self.error_class([place_overwrite_error])
                self._errors['placed_at'] = self.error_class([place_error])
        return self.cleaned_data


class BlockConfigForm(forms.Form, FormAdminDjango):

    config = ConfigFormField()
