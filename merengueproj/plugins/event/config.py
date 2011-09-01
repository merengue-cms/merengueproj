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

from merengue.collection.models import IncludeCollectionFilter
from merengue.collection.utils import create_normalize_collection
from merengue.pluggable import Plugin

from plugins.event.admin import EventAdmin, EventCategoryAdmin, EventSectionAdmin
from plugins.event.blocks import EventsCalendarBlock
from plugins.event.models import Event, Category
from plugins.event.viewlets import LatestEventViewlet, AllEventViewlet


class PluginConfig(Plugin):
    name = 'Events'
    description = 'Events plugin'
    version = '0.0.1a'
    url_prefixes = (
        ({'en': 'event',
          'es': 'eventos'},
          'plugins.event.urls'),
    )

    def models(self):
        return [
            (Event, EventAdmin),
            (Category, EventCategoryAdmin),
        ]

    def section_models(self):
        return [(Event, EventSectionAdmin)]

    def get_blocks(self):
        return [EventsCalendarBlock]

    def get_viewlets(self):
        return [LatestEventViewlet, AllEventViewlet]

    def post_install(self):
        collection = create_normalize_collection('event', u'Event', Event,
                                                 create_display_field=True,
                                                 create_filter_field=True)
