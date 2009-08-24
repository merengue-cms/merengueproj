from cmsutils.forms.fields import JSONFormField

from merengue.registry.widgets import ConfigWidget


class ConfigFormField(JSONFormField):

    def __init__(self, *args, **kwargs):
        kwargs['widget'] = ConfigWidget
        super(ConfigFormField, self).__init__(*args, **kwargs)
