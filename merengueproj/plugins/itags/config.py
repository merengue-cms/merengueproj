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

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from merengue.pluggable import Plugin
from merengue.registry import params

from plugins.itags.models import ITag
from plugins.itags.admin import ITagAdmin
from plugins.itags.viewlets import TagCloudViewlet
from plugins.itags.blocks import TagCloudBlock


class PluginConfig(Plugin):
    name = 'ITags'
    description = 'Internazionalized Tags'
    version = '0.0.1a'

    config_params = [
        params.Single(name='main_language', label=_('Main language for tags'), default=settings.LANGUAGE_CODE),
    ]

    url_prefixes = (
        ('itags', 'plugins.itags.urls'),
    )

    def get_model_admins(self):
        return [(ITag, ITagAdmin)]

    def get_viewlets(self):
        return [TagCloudViewlet]

    def get_blocks(self):
        return [TagCloudBlock]

    def post_install(self):
        from tagging.models import Tag
        [i.save() for i in Tag.objects.all()]
