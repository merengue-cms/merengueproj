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

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from merengue.registry.items import (RegistrableItem, RegistryError,
                            NotRegistered, AlreadyRegistered)
from merengue.registry.models import RegisteredItem
from merengue.registry.signals import item_registered, item_unregistered


def is_registered(item):
    """ Returns if a class is registered in some RegisteredItem """
    try:
        RegisteredItem.objects.get_by_item(item)
    except RegisteredItem.DoesNotExist:
        return False
    else:
        return True


def have_registered_items(item_class):
    """ Returns if a class is registered in some RegisteredItem """
    return bool(RegisteredItem.objects.by_item_class(item_class))


def is_broken(registered_item):
    """ Returns if registered item is broken (not exist in file system) """
    try:
        registered_item.get_registry_item()
    except (ImportError, TypeError, AttributeError):
        return True
    else:
        return False


def invalidate_registereditem():
    from merengue.cache import invalidate_johnny_cache
    from merengue.registry.models import RegisteredItem
    invalidate_johnny_cache(RegisteredItem)


def register(item_class, activate=None):
    """ Register a item in the registry """
    # all process will be in a unique transaction, we don't want to get
    # half committed

    if activate is None:
        activate = item_class.active_by_default

    if settings.CACHES['default']['BACKEND'].startswith('johnny'):
        invalidate_registereditem()

    sid = transaction.savepoint()
    try:
        if not issubclass(item_class, RegistrableItem):
            raise RegistryError('item class "%s" to be registered is not '
                                'a RegistrableItem subclass' % item_class)

        if item_class.singleton:
            # check not exists duplicated items
            if have_registered_items(item_class):
                raise AlreadyRegistered('item class "%s" is already registered'
                                        % item_class)
        registered_item = _register_new_item(item_class, activate)
    except:
        transaction.savepoint_rollback(sid)
        raise
    else:
        transaction.savepoint_commit(sid)
        item_registered.send(sender=item_class, registered_item=registered_item)
    return registered_item


def _register_new_item(item_class, activate):
    attributes = {
        'class_name': item_class.get_class_name(),
        'module': item_class.get_module(),
    }
    # Add attributes for extended class
    extended_attrs = item_class.get_extended_attrs()
    attributes.update(extended_attrs)
    registered_item = item_class.model.objects.create(**attributes)
    registered_item.category = item_class.get_category()
    registered_item.set_default_config(item_class)
    if activate:
        registered_item.activate()
    return registered_item


def unregister(item):
    try:
        registered_item = RegisteredItem.objects.get_by_item(item)
    except ObjectDoesNotExist:
        raise NotRegistered('item class "%s" is not registered' % item)
    registered_item.delete()
    item_unregistered.send(sender=item)


def unregister_all(item_class):
    for item in RegisteredItem.objects.by_item_class(item_class).get_items():
        unregister(item)


def get_item(item_class):
    return RegisteredItem.objects.get_by_item_class(item_class).get_registry_item()


def get_items(item_class):
    return RegisteredItem.objects.by_item_class(item_class).get_items()


def get_item_by_name(name):
    return RegisteredItem.objects.by_name(name=name).get_item()


def get_items_by_name(name):
    return RegisteredItem.objects.by_name(name=name).get_items()
