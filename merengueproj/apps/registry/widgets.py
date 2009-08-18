from django.template.loader import render_to_string

from cmsutils.forms.widgets import JSONWidget


class ConfigWidget(JSONWidget):

    def __init__(self, *args, **kwargs):
        super(ConfigWidget, self).__init__(*args, **kwargs)
        self.config = None # to be filled in registry model admin

    def render(self, name, value, attrs=None):
        return render_to_string('registry/configwidget.html',
                                {'config_params': self.config,
                                 'name': name,
                                 'value': value,
                                 'attrs': attrs})
