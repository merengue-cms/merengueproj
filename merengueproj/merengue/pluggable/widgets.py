# Copyright (c) 2010 by Yaco Sistemas
#
# This file is part of Merengue.
#
# Merengue is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Merengue is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Merengue.  If not, see <http://www.gnu.org/licenses/>.

from django.conf import settings
from django.utils.safestring import mark_safe

from merengue.registry.widgets import ConfigWidget


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
            plugin_text = unicode(plugin)
            if plugin_props:
                plugin_text += u" (%s)" % ', '.join(plugin_props)
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
