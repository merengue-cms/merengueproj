from cmsutils.forms.fields import JSONFormField

from merengue.registry.widgets import (ConfigWidget, RequiredPluginsWidget,
                                       RequiredAppsWidget)


class ConfigFormField(JSONFormField):

    def __init__(self, *args, **kwargs):
        super(ConfigFormField, self).__init__(*args, **kwargs)
        self.widget = ConfigWidget()


class RequiredPluginsFormField(JSONFormField):

    def __init__(self, *args, **kwargs):
        super(RequiredPluginsFormField, self).__init__(*args, **kwargs)
        self.widget = RequiredPluginsWidget()


class RequiredAppsFormField(JSONFormField):

    def __init__(self, *args, **kwargs):
        super(RequiredAppsFormField, self).__init__(*args, **kwargs)
        self.widget = RequiredAppsWidget()
