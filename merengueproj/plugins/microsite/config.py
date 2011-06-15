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

from merengue.urlresolvers import get_url_default_lang
from merengue.pluggable import Plugin

from plugins.microsite.models import MicroSite
from plugins.microsite.admin import MicroSiteAdmin


class PluginConfig(Plugin):
    name = 'Micro Sites'
    description = 'Microsite plugin'
    version = '0.0.1a'

    url_prefixes = (
        ({'en': 'microsite',
          'es': 'micrositios'},
             'plugins.microsite.urls'),
    )

    def models(self):
        return [(MicroSite, MicroSiteAdmin)]

    def get_section_prefixes(self):
        return (u'/%s/' % self.url_prefixes[0][0][get_url_default_lang()], )
