from django.db import transaction

from registry.items import (RegistryItem, RegistryError,
                            NotRegistered, AlreadyRegistered)


def register(item_class):
    """ register a item in the registry """
    # all process will be in a unique transaction, we don't want to get self committed
    transaction.commit_unless_managed()
    transaction.enter_transaction_management()
    transaction.managed(True)
    try:
        if not issubclass(item_class, RegistryItem):
            raise RegistryError('item class "%s" to be registered is not a RegistryItem subclass' % item_class)

        registered_item, created = item_class.model.objects.get_or_create(
            class_name=item_class.get_class_name(),
            module=item_class.get_module(),
        )
        if not created:
            raise AlreadyRegistered('item class "%s" is already registered' % item_class)
        registered_item.category = item_class.get_category()
        registered_item.set_default_config(item_class)
    except:
        transaction.rollback()
        raise
    else:
        transaction.commit()
    transaction.managed(False)


def unregister(item_class):
    try:
        registered_item = item_class.model.objects.get(name=item_class.name)
    except item_class.models.DoesNotExist:
        raise NotRegistered('item class "%s" is not registered' % item_class)
    registered_item.delete()
