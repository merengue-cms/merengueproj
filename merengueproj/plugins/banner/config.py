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

from merengue.collection.utils import create_normalize_collection
from merengue.pluggable import Plugin

from plugins.banner.admin import BannerAdmin, BannerCategoryAdmin, BannerSectionAdmin
from plugins.banner.blocks import BannerBlock, PortletBannerBlock
from plugins.banner.models import Banner, BannerCategory
from plugins.banner.viewlets import AllBannerViewlet


class PluginConfig(Plugin):
    name = 'Banner'
    description = 'Banner plugin'
    version = '0.0.1a'

    url_prefixes = (
        ('banners', 'plugins.banner.urls'),
    )

    def section_models(self):
        return [(Banner, BannerSectionAdmin)]

    def models(self):
        return [(Banner, BannerAdmin),
                (BannerCategory, BannerCategoryAdmin)]

    def get_blocks(self):
        return [BannerBlock, PortletBannerBlock]

    def get_viewlets(self):
        return [AllBannerViewlet]

    def post_install(self):
        create_normalize_collection('banners', u'Banners', Banner,
                                    create_display_field=True,
                                    create_filter_field=True)
