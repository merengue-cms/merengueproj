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
from django.core.exceptions import ObjectDoesNotExist


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

    def get_by_item(self, item_class):
        """ obtain registered item passing by param a RegistrableItem """
        for registered_item in self.all():
            if registered_item.module == item_class.get_module() and \
               registered_item.class_name == item_class.get_class_name():
                return registered_item
        raise ObjectDoesNotExist
