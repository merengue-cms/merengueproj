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

from plugins.banner.admin import BannerAdmin, BannerSectionAdmin
from plugins.banner.blocks import BannerBlock
from plugins.banner.models import Banner
from plugins.banner.viewlets import AllBannerViewlet


class PluginConfig(Plugin):
    name = 'Banner'
    description = 'Banner plugin'
    version = '0.0.1a'

    url_prefixes = (
        ('banners', 'plugins.banner.urls'),
    )

    @classmethod
    def section_models(cls):
        return [(Banner, BannerSectionAdmin)]

    @classmethod
    def get_model_admins(cls):
        return [(Banner, BannerAdmin), ]

    @classmethod
    def get_blocks(cls):
        return [BannerBlock]

    @classmethod
    def get_viewlets(cls):
        return [AllBannerViewlet]

    @classmethod
    def post_install(cls):
        create_normalize_collection('banners', u'Banners', Banner,
                                    create_display_field=True,
                                    create_filter_field=True)
