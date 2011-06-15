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

from merengue.pluggable import Plugin
from merengue.collection.utils import create_normalize_collection

from plugins.link.admin import LinkAdmin, LinkCategoryAdmin, LinkSectionAdmin
from plugins.link.models import Link, LinkCategory
from plugins.link.viewlets import LatestLinkViewlet, AllLinkViewlet


class PluginConfig(Plugin):
    name = 'Links'
    description = 'Links plugin'
    version = '0.0.1a'

    url_prefixes = (
        ({'en': 'link',
          'es': 'enlaces'},
         'plugins.link.urls'),
    )

    def section_models(self):
        return [(Link, LinkSectionAdmin)]

    def models(self):
        return [(Link, LinkAdmin),
                (LinkCategory, LinkCategoryAdmin)]

    def get_viewlets(self):
        return [LatestLinkViewlet, AllLinkViewlet]

    def post_install(self):
        create_normalize_collection(
            'links', u'Links', Link,
            create_display_field=True, create_filter_field=True)
