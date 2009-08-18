from cmsutils.forms.widgets import JSONWidget


class ConfigWidget(JSONWidget):

    def render(self, name, value, attrs=None):
        return super(ConfigWidget, self).render(name, value, attrs)
