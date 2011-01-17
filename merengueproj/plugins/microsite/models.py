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

from django.core.urlresolvers import reverse
from django.template.loader import render_to_string, TemplateDoesNotExist
from django.utils.importlib import import_module
from django.utils.translation import ugettext_lazy as _
from merengue.section.models import Section


class MicroSite(Section):

    def _content_public_link(self, section, content):
        url_external = reverse(content._public_link_without_section()[0],
                               args=content._public_link_without_section()[1])
        if url_external and url_external[0] == '/':
            url_external = url_external[1:]
        return ('microsite_url', [section.slug, url_external])

    def _menu_public_link(self, ancestors_path, menu):
        reverse_tuple = menu._menu_public_link_with_out_section(ancestors_path)
        url_external = reverse(reverse_tuple[0], args=reverse_tuple[1])
        if url_external and url_external[0] == '/':
            url_external = url_external[1:]
        return ('microsite_url', [self.slug, url_external])

    def url_in_section(self, url):
        return '/%s%s' % (self.slug, url)

    def custom_breadcrumbs(self, section, content):
        try:
            app_label = content._meta.app_label
            module_name = content._meta.module_name
            return render_to_string('%s/%s/section_breadcrumbs.html' % (app_label, module_name), {'section': section.real_instance})
        except TemplateDoesNotExist:
            try:
                plugin_config_path = "%s.config" % '.'.join(content.__module__.split(".")[:-1])
                plugin_config = import_module(plugin_config_path).PluginConfig
                verbose_name_model = content._meta.verbose_name
                url_model = "/%s/%s/" % (self.slug, plugin_config.url_prefixes[0][0])
            except ImportError:
                verbose_name_model = None
                url_model = None
            return render_to_string('microsite/breadcrumbs.html', {'section': section.real_instance,
                                                                   'verbose_name_model': verbose_name_model,
                                                                   'url_model': url_model})

    class Meta:
        verbose_name = _('microsite')
        verbose_name_plural = _('microsites')
