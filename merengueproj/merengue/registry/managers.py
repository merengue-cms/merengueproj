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

from django.db import models
from django.db.models.query import QuerySet

from cmsutils.utils import QuerySetWrapper

from merengue.cache import memoize, MemoizeCache


# ----- cache stuff -----

_registry_lookup_cache = MemoizeCache('registry_lookup_cache')


def _convert_cache_args(mem_args):
    item_class = mem_args[0]
    return ('%s.%s' % (item_class.get_module(), item_class.get_class_name()), )


def clear_lookup_cache():
    _registry_lookup_cache.clear()


# ----- querysets ------

class FakeRegisteredItemQuerySet(QuerySetWrapper):

    def __init__(self, items):
        super(FakeRegisteredItemQuerySet, self).__init__(items)
        if not hasattr(self, 'model'):
            from merengue.registry.models import RegisteredItem
            self.model = RegisteredItem

    def get_items(self):
        for item in self:
            yield item.get_registry_item()

    def get(self):
        try:
            return self[0]
        except IndexError:
            raise self.model.DoesNotExist()


class RegisteredItemQuerySet(QuerySet):

    def all(self):
        return self.filter(broken=False)

    def actives(self, ordered=False):
        """ Retrieves active items for site """
        if not ordered:
            return self.filter(active=True)
        else:
            return self.filter(active=True).order_by('order')

    def inactives(self, ordered=False):
        """ Retrieves inactive items for site """
        if not ordered:
            return self.exclude(active=True)
        else:
            return self.exclude(active=True).order_by('order')

    def with_brokens(self):
        return self.filter()

    def get_items(self):
        """ Returns registrable items (not registered items) """
        for item in self.filter():
            yield item.get_registry_item()

    def get_item(self):
        """ Returns the registrable item (not registered items) """
        return self.get().get_registry_item()

    def get_by_item(self, item):
        """ obtain registered item passing by param a RegistrableItem """
        return self.get(id=item.reg_item.id)

    def _by_item_class_func(self, item_class):
        items = []
        for item in self.all().order_by('-active'):
            if item.module == item_class.get_module() and item.class_name == item_class.get_class_name():
                items.append(item)
        return items
    _by_item_class = memoize(_by_item_class_func, _registry_lookup_cache, 2, offset=1, convert_args_func=_convert_cache_args, update_cache_if_empty=False)

    def get_by_item_class(self, item_class):
        """ obtain registered items passing by param a RegistrableItem class """
        try:
            return self._by_item_class(item_class)[0]
        except IndexError:
            raise self.model.DoesNotExist()

    def by_item_class(self, item_class):
        """ obtain registered items passing by param a RegistrableItem class """
        return FakeRegisteredItemQuerySet(self._by_item_class(item_class))

    def by_name(self, name):
        """ obtains registered items passing a full dotted name to RegistrableItem class """
        bits = name.split('.')
        module = '.'.join(bits[:-1])
        class_name = bits[-1]
        return self.filter(
            module=module,
            class_name=class_name,
        )


# ----- managers -----

class RegisteredItemManager(models.Manager):
    """ Registered item manager """

    def get_query_set(self):
        return RegisteredItemQuerySet(self.model)

    def with_brokens(self):
        return self.get_query_set().with_brokens()

    def actives(self, ordered=False):
        """ Retrieves active items for site """
        return self.get_query_set().actives(ordered)

    def inactives(self, ordered=False):
        """ Retrieves inactive items for site """
        return self.get_query_set().inactives(ordered)

    def get_by_item(self, item):
        """ obtain registered item passing by param a RegistrableItem """
        return self.get_query_set().get_by_item(item)

    def get_by_item_class(self, item_class):
        """ obtain registered item passing by param a RegistrableItem class """
        return self.get_query_set().get_by_item_class(item_class)

    def by_item_class(self, item_class):
        """ obtain registered items passing by param a RegistrableItem class """
        return self.get_query_set().by_item_class(item_class)

    def by_name(self, name):
        """ obtains registered items passing a full dotted name to RegistrableItem class """
        return self.get_query_set().by_name(name)
