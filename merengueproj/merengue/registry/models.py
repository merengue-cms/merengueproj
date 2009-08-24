from django.db import models
from django.utils.importlib import import_module

from merengue.registry.dbfields import ConfigField
from merengue.registry.managers import RegisteredItemManager


class RegisteredItem(models.Model):
    class_name = models.CharField(max_length=100, db_index=True)
    module = models.CharField(max_length=200, db_index=True)
    category = models.CharField(max_length=100, db_index=True)
    config = ConfigField()

    objects = RegisteredItemManager()

    def __unicode__(self):
        return self.class_name

    def set_default_config(self, item_class):
        if not self.config:
            self.config = {}
        for param in item_class.config_params:
            if param.has_default():
                self.config[param.name] = param.default
        self.save()

    def get_registry_item_class(self):
        module = import_module(self.module)
        return getattr(module, self.class_name)

    def get_config(self):
        parent_instance = getattr(self, 'registereditem_ptr', None)
        if parent_instance is not None:
            # because a inheritance JSONField problem
            return parent_instance.config
        else:
            return self.config
