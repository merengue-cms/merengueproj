# Copyright (c) 2011 by Yaco Sistemas
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

from plugins.twitter.blocks import UserTimelineBlock, HashtagTimelineBlock


class PluginConfig(Plugin):
    name = 'Twitter'
    description = 'Plugin to show a timeline of Twitter'
    version = '0.0.2a'
    required_apps = {'python-twitter': {}, }

    url_prefixes = (
        ('twitter', 'plugins.twitter.urls'),
        )

    def get_blocks(self):
        return [UserTimelineBlock, HashtagTimelineBlock]
