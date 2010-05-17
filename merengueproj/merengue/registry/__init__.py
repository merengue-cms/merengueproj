from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from merengue.registry.items import (RegistrableItem, RegistryError,
                            NotRegistered, AlreadyRegistered)
from merengue.registry.models import RegisteredItem
from merengue.registry.signals import item_registered, item_unregistered


def is_registered(item_class):
    """ Returns if a class is registered as RegisteredItem """
    try:
        RegisteredItem.objects.get_by_item(item_class)
    except ObjectDoesNotExist:
        return False
    else:
        return True


def is_broken(registered_item):
    """ Returns if registered item is broken (not exist in file system) """
    try:
        registered_item.get_registry_item_class()
    except (ImportError, TypeError):
        return True
    else:
        return False


def register(item_class, activate=False):
    """ Register a item in the registry """
    # all process will be in a unique transaction, we don't want to get
    # half committed
    sid = transaction.savepoint()
    try:
        if not issubclass(item_class, RegistrableItem):
            raise RegistryError('item class "%s" to be registered is not '
                                'a RegistrableItem subclass' % item_class)

        try:
            registered_item = item_class.model.objects.get_by_item(item_class)
        except ObjectDoesNotExist:
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
        else:
            raise AlreadyRegistered('item class "%s" is already registered'
                                    % item_class)
    except:
        transaction.savepoint_rollback(sid)
        raise
    else:
        transaction.savepoint_commit(sid)
        item_registered.send(sender=item_class, registered_item=registered_item)


def unregister(item_class):
    try:
        registered_item = RegisteredItem.objects.get_by_item(item_class)
    except ObjectDoesNotExist:
        raise NotRegistered('item class "%s" is not registered' % item_class)
    registered_item.delete()
    item_unregistered.send(sender=item_class)


def get_item(name, category):
    return RegisteredItem.objects.get(name=name, category=category)
