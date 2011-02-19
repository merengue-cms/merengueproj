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
from transmeta import get_real_fieldname_in_each_language

from plugins.standingout.admin import StandingOutAdmin, StandingOutCategoryAdmin, StandingSectionOutAdmin
from plugins.standingout.models import StandingOut, StandingOutCategory
from plugins.standingout.blocks import StandingOutBlock


class PluginConfig(Plugin):
    name = 'Standing out'
    description = 'Standing out plugin'
    version = '0.0.1a'

    url_prefixes = (
        ('standingout', 'plugins.standingout.urls'),
    )

    def get_blocks(self):
        return [StandingOutBlock]

    def section_models(self):
        return [(StandingOut, StandingSectionOutAdmin)]

    def post_install(self):
        soc_section = StandingOutCategory(context_variable='section', slug='section')
        for real_field in get_real_fieldname_in_each_language('name'):
            setattr(soc_section, real_field, 'section')
        soc_section.save()
        soc_content = StandingOutCategory(context_variable='content', slug='content')
        for real_field in get_real_fieldname_in_each_language('name'):
            setattr(soc_content, real_field, 'content')
        soc_content.save()

    def get_model_admins(self):
        return [(StandingOut, StandingOutAdmin),
                (StandingOutCategory, StandingOutCategoryAdmin)]
