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

import os
import shutil
from os import path

from django.conf import settings
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

    required_apps = ('oot', )

    def get_actions(self):
        return [ExportODT]

    def get_model_admins(self):
        return [(OpenOfficeTemplate, OpenOfficeTemplateAdmin)]

    def post_install(self):
        odt_path = path.join('oot', 'base.odt')
        try:
            OpenOfficeTemplate.objects.get(
                content_type=ContentType.objects.get_for_model(
                    BaseContent))
        except OpenOfficeTemplate.DoesNotExist:
            OpenOfficeTemplate.objects.create(
                title='BaseContent-template', template=odt_path,
                content_type=ContentType.objects.get_for_model(BaseContent),
                )
            src = path.join(settings.BASEDIR, settings.PLUGINS_DIR,
                            'odtexport', 'media', odt_path)
            dest = path.join(settings.MEDIA_ROOT, 'oot', 'base.odt')
            dest_dir = path.split(dest)[0]
            if path.exists(src):
                if not path.exists(dest_dir):
                    os.mkdir(dest_dir)
                if not path.exists(dest):
                    shutil.copyfile(src, dest)
