from cmsutils.db.fields import JSONField

from merengue.registry.fields import (ConfigFormField,
                                      RequiredPluginsFormField,
                                      RequiredAppsFormField)


class ConfigField(JSONField):

    def formfield(self, **kwargs):
        defaults = {'form_class': ConfigFormField}
        defaults.update(kwargs)
        return super(ConfigField, self).formfield(**defaults)


class RequiredPluginsField(JSONField):

    def formfield(self, **kwargs):
        defaults = {'form_class': RequiredPluginsFormField}
        defaults.update(kwargs)
        return super(RequiredPluginsField, self).formfield(**defaults)


class RequiredAppsField(JSONField):

    def formfield(self, **kwargs):
        defaults = {'form_class': RequiredAppsFormField}
        defaults.update(kwargs)
        return super(RequiredAppsField, self).formfield(**defaults)
