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

from django.db.models import signals
from django.utils.translation import ugettext_lazy as _

from merengue.registry.models import RegisteredItem
from merengue.registry import params
from merengue.registry.params import ConfigDict

from merengue.section.utils import get_section, filtering_in_section

# ---- Exception definitions ----


class AlreadyRegistered(Exception):
    pass


class NotRegistered(Exception):
    pass


class RegistryError(Exception):
    pass


# ---- Base classes ----


class RegistrableItem(object):
    """ Base class for all registered objects """

    name = None  # to be overriden in subclasses
    verbose_name = None  # to be overriden in subclasses
    help_text = None  # to be overriden in subclasses
    model = RegisteredItem  # to be overriden in subclasses
    config_params = []  # configuration parameters, to be overriden
    singleton = False  # only allow one registered item per class

    @classmethod
    def get_class_name(cls):
        return cls.__name__

    @classmethod
    def get_module(cls):
        return cls.__module__

    @classmethod
    def get_category(cls):
        return 'registryitem'

    @classmethod
    def get_extended_attrs(cls):
        return {}

    def __init__(self, reg_item):
        self.reg_item = reg_item

    def _config_dict(self, config):
        return ConfigDict(self.config_params, config)

    def get_config(self):
        registered_item = self.get_registered_item()
        return self._config_dict(registered_item.get_config())

    def get_merged_config(self, *configs):
        """ get a merged config with all config dicts passed by param """
        merged_config = self.get_config()
        for config in configs:
            if config:
                merged_config.update(config)
        return merged_config

    def get_registered_item(self):
        return self.reg_item

    def invalidate_cache(self):
        if hasattr(self, '_cached_registered_item'):
            del self._cached_registered_item


def _get_children_classes(content_type):
    subclasses = content_type.__subclasses__()
    result = []
    for subclass in subclasses:
        result += _get_children_classes(subclass)
        result += [subclass]
    return result


def _get_all_children_classes(content_type=None):
    if not content_type:  # to avoid circular import
        from merengue.base.models import BaseContent
        content_type = BaseContent
    return [(children_class._meta.module_name, children_class._meta.verbose_name)
            for children_class in _get_children_classes(content_type)]


class ContentTypeProvider(object):

    config_params = [
        params.List(
            name="contenttypes",
            label=_("Content types that whant to filter"),
            choices=_get_all_children_classes,
        ),
    ]


class ContentTypeFilterProvider(ContentTypeProvider):

    @classmethod
    def is_renderizable(cls, content_type):
        contenttypes_config = cls.get_config().get('contenttypes', None)
        if (not contenttypes_config or
            contenttypes_config.get_value() == params.NOT_PROVIDED):
            return True
        elif content_type:
            cts = contenttypes_config.get_value()
            return content_type.class_name in cts
        else:
            return False


class SectionFilterItemProvider(object):

    config_params = [
        params.Bool(
            name='filtering_section',
            label=_('If the collection is into a section, filter for the contents of this section'),
            default=True,
        ),
    ]


class ContentsItemProvider(object):

    def get_contents(self, request=None, context=None, section=None):
        raise NotImplementedError()


class QuerySetItemProvider(ContentsItemProvider, SectionFilterItemProvider):

    def _get_section(self, request, context):
        return get_section(request, context)

    def get_queryset(self, request=None, context=None):
        section = self._get_section(request, context)
        return self.queryset(request, context, section)

    def queryset(self, request=None, context=None, section=None):
        queryset = self.get_contents(request, context, section)
        if section and self.get_config().get('filtering_section', False).get_value():
            queryset = filtering_in_section(queryset, section)
        return queryset


class BlockQuerySetItemProvider(QuerySetItemProvider):

    def get_queryset(self, request=None, context=None):
        section = self._get_section(request, context)
        return self.queryset(request, context, section)

    def queryset(self, request=None, context=None, section=None):
        queryset = self.get_contents(request, context, section)
        if section and self.get_config().get('filtering_section', False).get_value():
            queryset = filtering_in_section(queryset, section)
        return queryset


class BlockSectionFilterItemProvider(SectionFilterItemProvider):
    pass


class ViewLetQuerySetItemProvider(QuerySetItemProvider):

    def _get_section(self, request, context):
        menu = context.get('menu', None)
        section = None
        if menu:
            section = menu.get_root().get_section()
        return section or super(ViewLetQuerySetItemProvider, self)._get_section(request, context)


def post_save_handler(sender, instance, **kwargs):
    if isinstance(instance, RegisteredItem):
        # cache invalidation of registered item in a registrable item
        instance.get_registry_item().invalidate_cache()


signals.post_save.connect(post_save_handler)
