# Copyright (c) 2010 by Yaco Sistemas <dgarcia@yaco.es>
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

from django.utils.translation import ugettext_noop as _

from merengue.pluggable import Plugin

from plugins.imagesize.models import ImageSize
from plugins.imagesize.admin import ImageSizeAdmin


class PluginConfig(Plugin):
    name = 'ImageSize'
    description = 'Notify when images exceed max size'
    version = '0.0.1a'

    url_prefixes = (
        ('imagesize', 'plugins.imagesize.urls'),
    )

    def get_model_admins(self):
        return [(ImageSize, ImageSizeAdmin)]

    def get_notifications(self):
        return [('imagesize_images', _('Images bigger thant expected'), _('Images bigger thant expected')),
                ('imagesize_broken', _("Image directory doesn't exists"), _("Image directory doesn't exists"))]
