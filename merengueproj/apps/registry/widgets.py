from django.forms import widgets
from django.forms.util import flatatt
from django.template.loader import render_to_string
from django.utils import simplejson as json
from django.utils.safestring import mark_safe


class ParamWidget(widgets.Widget):

    def __init__(self, param, attrs=None):
        super(ParamWidget, self).__init__(attrs)
        self.param = param

    def value_from_datadict(self, data, files, name):
        """ Returns a dictionary with only the value for widget param.
            ConfigWidget will compress all into a complete dictionary """
        if self.param.get_type() == 'List':
            value = data.getlist(name)
        else:
            value = data.get(name)
        return {self.param.name: value}

    def render(self, name, value, attrs=None):
        """ rendering function. note: value will be a config param instance """
        widget_attrs = self.build_attrs(attrs, name=name)
        return render_to_string('registry/paramwidget.html',
                                {'param': value,
                                 'name': name,
                                 'widget_attrs': mark_safe(flatatt(widget_attrs))})


class ConfigWidget(widgets.MultiWidget):

    def __init__(self, attrs=None):
        self.config = None # to be filled in registry model admin
        super(ConfigWidget, self).__init__(widgets=[], attrs=attrs)

    def add_config_widgets(self, config):
        self.config = config
        for param in self.config:
            self.widgets.append(ParamWidget(param))

    def decompress(self, value):
        if value:
            return [param for param in self.config]
        # if all None we returns n-Nones
        return [None]*len(self.widgets)

    def value_from_datadict(self, data, files, name):
        value_list = super(ConfigWidget, self).value_from_datadict(data, files, name)
        value = dict()
        for v in value_list:
            value.update(v)
        return json.dumps(value)

    def render(self, name, value, attrs=None):
        """ rendering function. note: value will be a config param instance """
        widgets_render = super(ConfigWidget, self).render(name, value, attrs)
        return mark_safe(widgets_render + \
                         u'<div><label>JSON Debug:</label><pre>%s</pre></div>' % value)
