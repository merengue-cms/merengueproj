# Copyright (c) 2010 by Yaco Sistemas <msaelices@yaco.es>
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

from os import path

from django.contrib.contenttypes.models import ContentType

from merengue.base.models import BaseContent
from merengue.pluggable import Plugin

from plugins.odtexport.actions import ExportODT
from plugins.odtexport.admin import OpenOfficeTemplateAdmin
from plugins.odtexport.models import OpenOfficeTemplate


class PluginConfig(Plugin):
    name = 'OpenOffice Export'
    description = 'ODT Exporter'
    version = '0.0.2'

    url_prefixes = (
        ('odtexport', 'plugins.odtexport.urls'),
    )

    @classmethod
    def get_actions(cls):
        return [ExportODT]

    @classmethod
    def get_model_admins(cls):
        return [(OpenOfficeTemplate, OpenOfficeTemplateAdmin)]

    @classmethod
    def hook_post_register(self):
        odt_path = path.join('media', 'oot', 'base.odt')
        try:
            OpenOfficeTemplate.objects.get(
                title='BaseContent-template', template=odt_path,
                content_type=ContentType.objects.get_for_model(BaseContent),
                )
        except OpenOfficeTemplate.DoesNotExist:
            OpenOfficeTemplate.objects.create(
                title='BaseContent-template', template=odt_path,
                content_type=ContentType.objects.get_for_model(BaseContent),
                )
