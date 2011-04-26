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

from django.utils.translation import ugettext_lazy as _

from merengue.pluggable import Plugin
from merengue.registry import params

from plugins.piwik.settings import PERIOD, DATE, METRIC
from plugins.piwik.blocks import PiwikBlock


class PluginConfig(Plugin):
    name = 'Piwik'
    description = 'Piwik integration plugin'
    version = '0.0.1'

    url_prefixes = (
        ({'en': 'stats',
          'es': 'estadisticas'},
             'plugins.piwik.urls'),
    )

    config_params = [
        params.Single(name='token', label=_('authentication token')),
        params.Single(name='url', label=_('piwik url')),
        params.Single(name='site_id', label=_('site id')),
        params.Single(name='metric', label=_('metric'), default=METRIC),
        params.Single(name='period', label=_('period'), default=PERIOD),
        params.Single(name='date', label=_('date'), default=DATE),
    ]

    def get_actions(self):
        return []

    def get_blocks(self):
        return [PiwikBlock]

    def section_models(self):
        return []

    def get_perms(self):
        return [('View all stats', 'view_all_stats'),
                ('View my stats', 'view_my_stats')]
