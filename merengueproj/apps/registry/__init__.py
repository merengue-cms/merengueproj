from registry.base import (RegistryItem, RegistryError,
                           NotRegistered, AlreadyRegistered)


def register(item):
    if not isinstance(item, RegistryItem):
        raise RegistryError('item to be registered is not a RegistryItem instance')
    registered_item, created = item.model.objects.get_or_create(
        class_name=item.get_class_name(),
        module=item.get_module(),
    )
    if not created:
        raise AlreadyRegistered('item "%s" is already registered' % item)
    registered_item.category = item.get_category()
    registered_item.set_default_config(item)


def unregister(item):
    try:
        registered_item = item.model.objects.get(name=item.name)
    except item.models.DoesNotExist:
        raise NotRegistered('item "%s" is not registered' % item)
    registered_item.delete()
