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
from django.forms.util import ErrorList
from django.utils.importlib import import_module
from django.utils.translation import ugettext_lazy as _

from autoreports.forms import FormAdminDjango

from merengue.base.models import BaseContent
from merengue.base.forms import BaseAdminModelForm, BaseForm
from merengue.block.blocks import ContentBlock, SectionBlock
from merengue.block.models import RegisteredBlock
from merengue.pluggable.models import RegisteredPlugin
from merengue.registry import register
from merengue.registry.fields import ConfigFormField
from merengue.section.models import BaseSection


class BaseContentRelatedBlockAddForm(forms.ModelForm):
    """
    Form for adding blocks related to one content in the admin page
    """
    block_class = forms.ChoiceField(
        label=_('Block to add'),
    )

    def __init__(self, *args, **kwargs):
        super(BaseContentRelatedBlockAddForm, self).__init__(*args, **kwargs)
        active_plugins = RegisteredPlugin.objects.actives().get_items()
        blocks_classes = []
        for plugin in active_plugins:
            addable_blocks = [b for b in plugin.get_blocks() if b.is_addable]
            blocks_classes.extend(addable_blocks)
        self.fields['block_class'].choices = [
            ('%s.%s' % (b.get_module(), b.get_class_name()), b.verbose_name) for b in blocks_classes
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

    class Meta:
        model = RegisteredBlock
        fields = ('block_class', )


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
            place_overwrite_error = _("Unmark this field to keep the block in the specified place (even though it won't be displayed)")
            noeffect_error = _("A block is already set to overwrite others of this kind. Unmark this to save the block, even though it won't be displayed")
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


class AddBlockForm(BaseForm):

    block_type = forms.ChoiceField(choices=[], label=_('Select block type'), required=True)
    place = forms.CharField(widget=forms.HiddenInput)
    contentid = forms.CharField(widget=forms.HiddenInput, required=False)
    sectionid = forms.CharField(widget=forms.HiddenInput, required=False)
    scope = forms.ChoiceField(label=_('Scope'), widget=forms.RadioSelect, initial='global')

    def _find_subclasses(self, base, subclasses=None):
        subclasses = subclasses or []
        for i in base.__subclasses__():
            if i not in subclasses:
                subclasses.append(i)
                self._find_subclasses(i, subclasses)
        return subclasses

    def __init__(self, *args, **kwargs):
        super(AddBlockForm, self).__init__(*args, **kwargs)
        choices = []
        scopes = [('global', _(u'Global'))]
        section_id = self.initial.get('sectionid', None) or self.data.get('sectionid', None)
        section = None
        if section_id:
            try:
                section = BaseSection.objects.get(id=section_id)
                section = section.get_real_instance()
                scopes += [('section', _(u'Section: %(section)s') % {'section': section})]
            except BaseSection.objects.DoesNotExist:
                pass
        content_id = self.initial.get('contentid', None) or self.data.get('contentid', None)
        content = None
        if content_id:
            try:
                content = BaseContent.objects.get(id=content_id)
                content = content.get_real_instance()
                scopes += [('content', _(u'Content: %(content)s') % {'content': content})]
            except BaseContent.objects.DoesNotExist:
                pass
        blocks = []
        content_blocks = []
        section_blocks = []
        for plugin in RegisteredPlugin.objects.actives():
            addable_blocks = [b for b in plugin.get_registry_item().get_blocks() if b.is_addable]
            for block in addable_blocks:
                if issubclass(block, SectionBlock):
                    if not section:
                        continue
                    else:
                        section_blocks.append(block)
                elif issubclass(block, ContentBlock):
                    if not content:
                        continue
                    else:
                        content_blocks.append(block)
                else:
                    blocks.append(block)
        if blocks:
            block_list = [('%s.%s' % (i.__module__, i.__name__), i.verbose_name) for i in blocks]
            block_list.sort(lambda x, y: cmp(x[1], y[1]))
            choices.append((_(u'Blocks'), block_list))
        if content_blocks:
            block_list = [('%s.%s' % (i.__module__, i.__name__), i.verbose_name) for i in content_blocks]
            block_list.sort(lambda x, y: cmp(x[1], y[1]))
            choices.append((_(u'Content blocks'), block_list))
        if section_blocks:
            block_list = [('%s.%s' % (i.__module__, i.__name__), i.verbose_name) for i in section_blocks]
            block_list.sort(lambda x, y: cmp(x[1], y[1]))
            choices.append((_(u'Section blocks'), block_list))
        self.fields['block_type'].choices = choices
        self.fields['scope'].choices = scopes
        self.tie_render = None

    def check_scope(self, content=None, section=None):
        if self.cleaned_data['scope'] == 'section':
            if not section:
                self._errors['scope'] = ErrorList([_(u'You can not select section scope cause your are not inside a section')])
            else:
                self.tie_render = section
        elif self.cleaned_data['scope'] == 'content':
            if not content:
                self._errors['scope'] = ErrorList([_(u'You can not select content scope cause your are not inside a content')])
            else:
                self.tie_render = content

        if issubclass(self.block_class, ContentBlock):
            if not content:
                self._errors['block_type'] = ErrorList([_(u'You can not insert a content block from a view without content')])
            else:
                self.tie_render = content

    def check_block_type(self, content=None, section=None):
        block_type = self.cleaned_data['block_type']

        module, classname = block_type.rsplit('.', 1)
        block_class = getattr(import_module(module), classname)
        self.block_class = block_class

        if issubclass(self.block_class, SectionBlock):
            if not section:
                self._errors['block_type'] = ErrorList([_(u'You can not insert a section block from a view without section')])
            else:
                self.tie_render = section

    def clean(self):
        content = None
        content_id = self.cleaned_data.get('contentid', None)
        if content_id:
            try:
                content = BaseContent.objects.get(id=content_id).get_real_instance()
            except BaseContent.DoesNotExist:
                pass

        section = None
        section_id = self.cleaned_data.get('sectionid', None)
        if section_id:
            try:
                section = BaseSection.objects.get(id=section_id).get_real_instance()
            except BaseSection.DoesNotExist:
                pass

        self.check_block_type(content, section)
        self.check_scope(content, section)
        return self.cleaned_data

    def save(self):
        place = self.cleaned_data['place']
        reg_block = register(self.block_class)
        reg_block.active = True
        if self.cleaned_data['scope'] in ('content', 'section'):
            reg_block.content = self.tie_render
        reg_block.placed_at = place
        reg_block.save()
        reg_block.tied = self.tie_render
        return reg_block
