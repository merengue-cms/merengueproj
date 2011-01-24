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

    name = None # to be overriden in subclasses
    verbose_name = None # to be overriden in subclasses
    help_text = None # to be overriden in subclasses
    model = RegisteredItem # to be overriden in subclasses
    config_params = [] # configuration parameters, to be overriden

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
    def get_config(cls):
        registered_item = cls.get_registered_item()
        return ConfigDict(cls.config_params, registered_item.get_config())

    @classmethod
    def get_registered_item(cls):
        for registered_item in cls.model.objects.all():
            # note: we do not use get to use cache from caching manager
            if registered_item.module == cls.get_module() and \
               registered_item.class_name == cls.get_class_name():
                return registered_item
        raise ObjectDoesNotExist

    @classmethod
    def get_extended_attrs(cls):
        return {}


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


class BlockQuerySetItemProvider(QuerySetItemProvider):
    pass


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

"""
Example use::

class Action(RegistrableItem):
    model = RegisteredAction

    @classmethod
    def get_category(cls):
        return 'action'

class PDFExport(Action):
    name = "pdfexport"

    config_params = params.Single(name='pdfbin', default='/usr/bin/html2pdf')

>>> from merengue.pluggable.pdfexport.actions import PDFExport
>>> PDFExport.get_config()['pdfbin']
"""
