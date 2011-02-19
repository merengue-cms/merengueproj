# Copyright (c) 2010 by Yaco Sistemas <dgarcia@yaco.es>
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

from merengue.pluggable import Plugin

from plugins.oldbrowser.models import OldBrowser
from plugins.oldbrowser.admin import OldBrowserAdmin
from plugins.oldbrowser.blocks import OldBrowserBlock


class PluginConfig(Plugin):
    name = 'Old Browser'
    description = 'Notify old browser plugin'
    version = '0.0.1'

    url_prefixes = (
        ({'en': 'oldbrowser',
          'es': 'navegador_antiguo'},
         'plugins.oldbrowser.urls'),
    )

    def get_actions(self):
        return []

    def get_model_admins(self):
        return [(OldBrowser, OldBrowserAdmin)]

    def get_blocks(self):
        return [OldBrowserBlock]
