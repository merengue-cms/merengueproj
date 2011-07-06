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
from transmeta import get_fallback_fieldname

from plugins.standingout.admin import StandingOutAdmin, StandingOutCategoryAdmin
from plugins.standingout.models import StandingOut, StandingOutCategory
from plugins.standingout.blocks import StandingOutBlock, StandingOutSlideShowBlock


class PluginConfig(Plugin):
    name = 'Standing out'
    description = 'Standing out plugin'
    version = '0.0.1a'

    url_prefixes = (
        ({'en': 'standingout',
          'es': 'destacados'}, 'plugins.standingout.urls'),
    )

    def get_blocks(self):
        return [StandingOutBlock, StandingOutSlideShowBlock]

    def post_install(self):
        name_field = get_fallback_fieldname('name')
        for slug in ('section', 'content', 'slideshow'):
            if not StandingOutCategory.objects.filter(slug=slug).exists():
                standingout_category = StandingOutCategory(context_variable=slug, slug=slug)
                setattr(standingout_category, name_field, slug)
                standingout_category.save()

    def models(self):
        return [(StandingOut, StandingOutAdmin)]

    def get_model_admins(self):
        return [(StandingOutCategory, StandingOutCategoryAdmin)]
