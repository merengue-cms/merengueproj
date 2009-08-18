from django.db import models

from registry.dbfields import ConfigField


class RegisteredItem(models.Model):
    class_name = models.CharField(max_length=100, db_index=True)
    module = models.CharField(max_length=200, db_index=True)
    category = models.CharField(max_length=100, db_index=True)
    config = ConfigField()

    def __unicode__(self):
        return self.class_name

    def set_default_config(self, item):
        for param in item.config_params:
            self.config[param.name] = {
                'module': param.get_type(),
            }
            if param.has_default():
                self.config['value'] = param.default
        self.save()
