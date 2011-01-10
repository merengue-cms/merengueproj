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
from django.utils.translation import ugettext_lazy as _

from merengue.pluggable import Plugin
from merengue.registry import params

from plugins.standingout.admin import StandingOutAdmin, StandingOutCategoryAdmin
from plugins.standingout.models import StandingOut, StandingOutCategory
from plugins.standingout.blocks import StandingOutBlock


class PluginConfig(Plugin):
    name = 'Standing out'
    description = 'Standing out plugin'
    version = '0.0.1a'

    config_params = [
        params.Integer(name='limit', label=_('limit for standingouts in block'), default='5'),
    ]

    url_prefixes = (
        ('standingout', 'plugins.standingout.urls'),
    )

    @classmethod
    def get_blocks(cls):
        return [StandingOutBlock]

    @classmethod
    def section_models(cls):
        return []

    @classmethod
    def get_model_admins(cls):
        return [(StandingOut, StandingOutAdmin), (StandingOutCategory, StandingOutCategoryAdmin)]
