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

from plugins.filebrowser.models import Repository, Document
from plugins.filebrowser.admin import RepositoryModelAdmin, DocumentModelAdmin, RepositorySectionModelAdmin


class PluginConfig(Plugin):
    name = 'File browser'
    description = 'File browser plugin'
    version = '0.0.1a'

    config_params = [
        params.Single(name='filebrowser_root', label=_('Root below MEDIA_ROOT'), default='filebrowser'),
        params.Single(name='filebrowser_docs_root', label=_('Docs root below MEDIA_ROOT'), default='filebrowser_docs'),
        params.Single(name='filebrowser_docs_url', label=_('Docs url below MEDIA_URL'), default='filebrowser_docs/'),
    ]

    url_prefixes = (
        ({'en': 'filebrowser',
          'es': 'navegador_de_ficheros'},
          'plugins.filebrowser.urls'),
    )

    def models(self):
        return [(Repository, RepositoryModelAdmin),
                (Document, DocumentModelAdmin)]

    def section_models(self):
        return [(Repository, RepositorySectionModelAdmin)]
