from cmsutils.db.fields import JSONField

from merengue.registry.fields import ConfigFormField


class ConfigField(JSONField):

    def formfield(self, **kwargs):
        defaults = {'form_class': ConfigFormField}
        defaults.update(kwargs)
        return super(ConfigField, self).formfield(**defaults)
