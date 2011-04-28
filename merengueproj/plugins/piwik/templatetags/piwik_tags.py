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

from django import template

from merengue.pluggable.utils import get_plugin
from merengue.section.models import BaseSection

from plugins.piwik.settings import CUSTOM_VARIABLES
from plugins.piwik.utils import SECTION_PIWIK_VARIABLE, CONTENT_PIWIK_VARIABLE, get_contents

register = template.Library()


@register.inclusion_tag('piwik/javascript.html', takes_context=True)
def piwik_script(context):
    plugin_config = get_plugin('piwik').get_config()
    url = plugin_config.get('url').get_value()
    token = plugin_config.get('token').get_value()
    site_id = plugin_config.get('site_id').get_value()
    return {'url': url,
            'token': token,
            'site_id': site_id,
            'section_piwik_variable': SECTION_PIWIK_VARIABLE,
            'content_piwik_variable': CONTENT_PIWIK_VARIABLE,
            'section': context.get('section'),
            'content': context.get('content'),
            'custom_variables': CUSTOM_VARIABLES,
            'request': context.get('request')}


@register.inclusion_tag('piwik/contents_stats.html', takes_context=True)
def contents_stats(context, username=None, expanded=1):
    basecontents = get_contents(username, expanded)
    contents = [content for content in basecontents if not isinstance(content[0].get_real_instance(), BaseSection)]
    sections = [content for content in basecontents if isinstance(content[0].get_real_instance(), BaseSection)]
    return {'contents': contents,
            'sections': sections,
            'request': context.get('request')}
