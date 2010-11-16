# Copyright (c) 2010 by Yaco Sistemas <msaelices@yaco.es>
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

from plugins.rss.actions import GenerateRSS


class PluginConfig(Plugin):
    name = 'RSS syndication'
    description = 'Plugin to allow RSS syndication of contents'
    version = '0.0.1a'

    url_prefixes = (
        ('rss', 'plugins.rss.urls'),
    )

    config_params = [
        params.List(name="contenttypes",
                    label=_("Content types that whant to be syndicated")),
        params.Single(name="limit",
                      label=_("number of elements to show at the feed"),
                      default=10),
    ]

    @classmethod
    def get_actions(cls):
        return [GenerateRSS]

    @classmethod
    def get_model_admins(cls):
        return []
