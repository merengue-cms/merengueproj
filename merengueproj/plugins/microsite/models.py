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
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from merengue.section.models import BaseSection


class MicroSite(BaseSection):

    def _content_public_link(self, section, content):
        url_external = reverse(content._public_link_without_section()[0],
                               args=content._public_link_without_section()[1])
        if url_external and url_external[0] == '/':
            url_external = url_external[1:]
        return ('microsite_url', [section.slug, url_external])

    def _document_public_link(self, section, content):
        return ('document_microsite_view', [section.slug, content.pk, content.slug])

    def _menu_public_link(self, ancestors_path, menu):
        reverse_tuple = menu._menu_public_link_without_section(ancestors_path)
        url_external = reverse(reverse_tuple[0], args=reverse_tuple[1])
        if url_external and url_external[0] == '/':
            url_external = url_external[1:]
        return ('microsite_url', [self.slug, url_external])

    def url_in_section(self, url):
        return '/%s%s' % (self.slug, url)

    def breadcrumbs(self, content=None):
        if not content:
            # breadcrumbs end here
            return super(MicroSite, self).breadcrumbs()
        url_section = super(MicroSite, self).breadcrumbs_items()
        for name, url in content.breadcrumbs_items():
            if url and url[0] == '/':
                url = url[1:]
            url_section.append((name, reverse("microsite_url", args=(self.slug, url))))
        if url_section:
            url_section[-1] = (url_section[-1][0], '')
        return render_to_string('microsite/breadcrumbs.html', {
            'section': self,
            'urls': url_section,
        })

    def _public_link_without_section(self):
        return ('microsite_view', (self.slug, ))

    class Meta:
        verbose_name = _('microsite')
        verbose_name_plural = _('microsites')
        check_slug_uniqueness = True
