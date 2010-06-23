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

from django.conf import settings
from django.utils import translation

from merengue.pluggable.loading import load_plugins, plugins_loaded


class ActivePluginsMiddleware(object):

    def process_request(self, request):
        if request.get_full_path().startswith(settings.MEDIA_URL):
            return None # plugin activation is not needed on static files
        if not plugins_loaded():
            load_plugins()
            # reset all i18n catalogs to load plugin ones
            if settings.USE_I18N:
                lang = translation.get_language()
                translation.trans_real._translations = {}
                translation.deactivate()
                translation.activate(lang)
        return None
