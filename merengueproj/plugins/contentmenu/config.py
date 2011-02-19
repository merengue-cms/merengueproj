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

from plugins.contentmenu.admin import ContentGroupAdmin
from plugins.contentmenu.blocks import ContentGroupLinksBlock
from plugins.contentmenu.models import ContentGroup


class PluginConfig(Plugin):
    name = 'Content menu'
    description = 'Plugin to associate some contents between them'
    version = '0.0.1a'

    config_params = [
        params.PositiveInteger(
            name="numchars",
            label=_("number of chars that should have the link as maximum"),
            default=15,
        ),
    ]

    def get_blocks(self):
        return [ContentGroupLinksBlock, ]

    def get_model_admins(self):
        return [(ContentGroup, ContentGroupAdmin)]
