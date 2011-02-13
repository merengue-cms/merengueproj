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

    def by_item_class(self, item_class):
        """ obtain registered items passing by param a RegistrableItem class """
        return self.filter(
            module=item_class.get_module(),
            class_name=item_class.get_class_name(),
        )

    def by_name(self, name):
        """ obtains registered items passing a full dotted name to RegistrableItem class """
        bits = name.split('.')
        module = '.'.join(bits[:-1])
        class_name = bits[-1]
        return self.filter(
            module=module,
            class_name=class_name,
        )


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

    def by_item_class(self, item_class):
        """ obtain registered items passing by param a RegistrableItem class """
        return self.get_query_set().by_item_class(item_class)

    def by_name(self, name):
        """ obtains registered items passing a full dotted name to RegistrableItem class """
        return self.get_query_set().by_name(name)
