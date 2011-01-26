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

from django.core.exceptions import ObjectDoesNotExist
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
    def _config_dict(cls, config):
        return ConfigDict(cls.config_params, config)

    @classmethod
    def get_config(cls):
        registered_item = cls.get_registered_item()
        return cls._config_dict(registered_item.get_config())

    @classmethod
    def get_merged_config(cls, *configs):
        """ get a merged config with all config dicts passed by param """
        merged_config = cls.get_config()
        for config in configs:
            if config:
                merged_config.update(config)
        return merged_config

    @classmethod
    def get_registered_item(cls):
        if hasattr(cls, '_cached_registered_item'):
            return cls._cached_registered_item
        for registered_item in cls.model.objects.all():
            # note: we do not use get to use cache from caching manager
            if registered_item.module == cls.get_module() and \
               registered_item.class_name == cls.get_class_name():
                cls._cached_registered_item = registered_item
                return registered_item
        raise ObjectDoesNotExist

    @classmethod
    def get_extended_attrs(cls):
        return {}

    @classmethod
    def invalidate_cache(cls):
        if hasattr(cls, '_cached_registered_item'):
            del cls._cached_registered_item


class SectionFilterItemProvider(object):

    config_params = [
        params.Bool(
            name='filtering_section',
            label=_('If the collection is into a section, filter for the contents of this section'),
            default=True,
        ),
    ]


class ContentsItemProvider(object):

    @classmethod
    def get_contents(cls, request=None, context=None, section=None):
        raise NotImplementedError()


class QuerySetItemProvider(ContentsItemProvider, SectionFilterItemProvider):

    @classmethod
    def _get_section(cls, request, context):
        return get_section(request, context)

    @classmethod
    def get_queryset(cls, request=None, context=None):
        section = cls._get_section(request, context)
        return cls.queryset(request, context, section)

    @classmethod
    def queryset(cls, request=None, context=None, section=None):
        queryset = cls.get_contents(request, context, section)
        if section and cls.get_config().get('filtering_section', False).get_value():
            queryset = filtering_in_section(queryset, section)
        return queryset


class BlockQuerySetItemProvider(QuerySetItemProvider):

    @classmethod
    def get_queryset(cls, request=None, context=None,
                     block_content_relation=None):
        section = cls._get_section(request, context)
        return cls.queryset(request, context, section, block_content_relation)

    @classmethod
    def queryset(cls, request=None, context=None, section=None,
                 block_content_relation=None):
        queryset = cls.get_contents(request, context, section,
                                    block_content_relation)
        if section and cls.get_config().get('filtering_section', False).get_value():
            queryset = filtering_in_section(queryset, section)
        return queryset


class BlockSectionFilterItemProvider(SectionFilterItemProvider):
    pass


class ViewLetQuerySetItemProvider(QuerySetItemProvider):

    @classmethod
    def _get_section(cls, request, context):
        menu = context.get('menu', None)
        section = None
        if menu:
            section = menu.get_root().get_section()
        return section or super(ViewLetQuerySetItemProvider, cls)._get_section(request, context)


def post_save_handler(sender, instance, **kwargs):
    if isinstance(instance, RegisteredItem):
        # cache invalidation of registered item in a registrable intem
        instance.get_registry_item_class().invalidate_cache()


signals.post_save.connect(post_save_handler)
