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

from plugins.googlesearch.blocks import GoogleSearchBlock


class PluginConfig(Plugin):
    name = 'Google search'
    description = 'Google search plugin'
    version = '0.0.1a'

    config_params = [
        params.Single(name='custom_search_control', label=_('Custom search control'), default='003808332573069177904:wm3_yobt584'),
        params.Single(name='language', label=_('language'), default='es'),
        params.Single(name='search_result_content', label=_('Search result content (element\'s id of DOM)'), default='content'),
        params.Single(name='search_form_content', label=_('Search form content (element\'s id of DOM)'), default='cse'),
    ]

    @classmethod
    def get_blocks(cls):
        return [GoogleSearchBlock]
