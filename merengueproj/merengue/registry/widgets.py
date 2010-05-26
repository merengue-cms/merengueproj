from django.conf import settings
from django.forms import widgets
from django.forms.util import flatatt
from django.template.loader import render_to_string
from django.utils import simplejson as json
from django.utils.html import linebreaks
from django.utils.safestring import mark_safe


class ParamWidget(widgets.Widget):

    def __init__(self, param, attrs=None):
        super(ParamWidget, self).__init__(attrs)
        self.param = param

    def value_from_datadict(self, data, files, name):
        """ Returns a dictionary with only the value for widget param.
            ConfigWidget will compress all into a complete dictionary """
        value = self.param.get_value_from_datadict(data, name)
        return {self.param.name: value}

    def render(self, name, value, attrs=None):
        """ rendering function. note: value will be a config param instance """
        widget_attrs = self.build_attrs(attrs, name=name)
        flat_attrs = flatatt(widget_attrs)
        return render_to_string('registry/paramwidget.html',
                                {'param': value,
                                 'name': name,
                                 'widget_attrs': mark_safe(flat_attrs)})


class ConfigWidget(widgets.MultiWidget):

    def __init__(self, attrs=None):
        self.config = None # to be filled in registry model admin
        super(ConfigWidget, self).__init__(widgets=[], attrs=attrs)

    def add_config_widgets(self, config):
        self.config = config
        for param in self.config.values():
            self.widgets.append(ParamWidget(param))

    def decompress(self, value):
        if value and getattr(self.config, 'values', []):
            return [param for param in self.config.values()]
        # if all None we returns n-Nones
        return [None]*len(self.widgets)

    def value_from_datadict(self, data, files, name):
        value_list = super(ConfigWidget, self).value_from_datadict(data,
                                                                   files, name)
        value = dict()
        for v in value_list:
            value.update(v)
        return json.dumps(value)

    def render(self, name, value, attrs=None):
        """ rendering function. note: value will be a config param instance """
        widgets_render = super(ConfigWidget, self).render(name, value, attrs)
        json_value = linebreaks(json.dumps(value, indent=2))
        return mark_safe(widgets_render + \
            u"""<div style="clear: both;">
                    <label>JSON Debug:</label>
                    <pre>%s</pre>
                </div>""" % json_value)


class RequiredPluginsWidget(ConfigWidget):

    def render(self, name, value, attrs=None):
        """ rendering function. """
        required_plugins = value or {}
        plugins_li = []
        from merengue.pluggable.models import RegisteredPlugin
        for plugin, properties in required_plugins.iteritems():
            filter_plugins = {'directory_name': plugin, 'active': True}
            # HACK: Key for filter params dict can't be unicode strings
            for attr, value in properties.iteritems():
                filter_plugins.update({str(attr): value})
            plugin_props = ["%s: %s" % (k, v)
                            for k, v in properties.iteritems()]
            plugin_text = u"%s (%s)" % (plugin, ', '.join(plugin_props))
            if RegisteredPlugin.objects.filter(**filter_plugins):
                plugins_li.append(u"<li class='fulfilled'>%s</li>" \
                                  % plugin_text)
            else:
                plugins_li.append(u"<li class='unfulfilled'>%s</li>"
                                  % plugin_text)
        out = None
        if plugins_li:
            out = u"<ul class='dependencies'>%s</ul>" % ''.join(plugins_li)
        return mark_safe(out)


class RequiredAppsWidget(ConfigWidget):

    def render(self, name, value, attrs=None):
        """ rendering function. """
        required_apps = value or []
        plugins_li = []
        for app in required_apps:
            if app in settings.INSTALLED_APPS:
                plugins_li.append(u"<li class='fulfilled'>%s</li>" % app)
            else:
                plugins_li.append(u"<li class='unfulfilled'>%s</li>" % app)
        out = None
        if plugins_li:
            out = u"<ul class='dependencies'>%s</ul>" % ''.join(plugins_li)
        return mark_safe(out)
