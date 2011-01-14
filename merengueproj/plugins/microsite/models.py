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
from django.utils.translation import ugettext_lazy as _
from merengue.section.models import Section


class MicroSite(Section):

    def content_public_link(self, section, content):
        url_external = reverse(content._public_link_without_section()[0],
                               args=content._public_link_without_section()[1])
        if url_external and url_external[0] == '/':
            url_external = url_external[1:]
        return ('microsite_url', [section.slug, url_external])

    class Meta:
        verbose_name = _('microsite')
        verbose_name_plural = _('microsites')
