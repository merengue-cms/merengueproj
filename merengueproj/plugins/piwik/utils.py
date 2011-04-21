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

import re
from operator import itemgetter

from merengue.pluggable.utils import get_plugin
from merengue.base.models import BaseContent

from plugins.piwik.api import PiwikAPI
from plugins.piwik.settings import PERIOD, DATE, METRIC

# don't change, this is used to track stats in piwik by javascript
# if you change it, stats in piwik can be changed
SECTION_PIWIK_VARIABLE = 'Secciones'
CONTENT_PIWIK_VARIABLE = 'Contenidos'

_piwik_api = None


def get_plugin_config():
    return get_plugin('piwik').get_config()


def get_piwik_api(reload=True):
    global _piwik_api
    if _piwik_api is None or reload:
        plugin_config = get_plugin_config()
        url = plugin_config.get('url').get_value()
        token = plugin_config.get('token').get_value()

        _piwik_api = PiwikAPI(url, token)

    return _piwik_api


def get_period():
    plugin_config = get_plugin_config()
    return plugin_config.get('period').get_value() or PERIOD


def get_date():
    plugin_config = get_plugin_config()
    return plugin_config.get('date').get_value() or DATE


def get_metric():
    plugin_config = get_plugin_config()
    return plugin_config.get('metric').get_value() or METRIC


def get_site_id():
    plugin_config = get_plugin_config()
    return plugin_config.get('site_id').get_value()


def get_piwik_url():
    plugin_config = get_plugin_config()
    return plugin_config.get('url').get_value()


def get_token():
    plugin_config = get_plugin_config()
    return plugin_config.get('token').get_value()


def get_variable_stats(custom_variable):
    id_subtable = None
    data = []
    piwik_api = get_piwik_api()
    site_id = get_site_id()
    period = get_period()
    date = get_date()
    variables_data = piwik_api.call('CustomVariables.getCustomVariables',
                                    params={'idSite': site_id,
                                            'period': period,
                                            'date': date}, format='json')

    for variable in variables_data:
        if variable['label'] == custom_variable:
            id_subtable = variable['idsubdatatable']
            break

    if id_subtable:
        data = piwik_api.call('CustomVariables.getCustomVariablesValuesFromNameId',
                              params={'idSite': site_id,
                                      'period': period,
                                      'date': date,
                                      'idSubtable': id_subtable}, format='json')
    return data


def get_basecontents(data=None):
    pattern = ".*id:(\d).*"
    contents = {}
    metric = get_metric()
    for entry in data:
        match = re.match(pattern, entry['label'])
        id = None
        if match:
            id = match.groups()[0]
        if id:
            content = BaseContent.objects.get(id=id)
            if content in contents:
                contents[content] = contents[content] + entry[metric]
            else:
                contents[content] = entry[metric]
    return contents


def sort_contents(contents):
    return sorted(contents.iteritems(), key=itemgetter(1), reverse=True)


def get_contents():
    data = get_variable_stats(CONTENT_PIWIK_VARIABLE)
    return sort_contents(get_basecontents(data))


def get_sections():
    data = get_variable_stats(SECTION_PIWIK_VARIABLE)
    return sort_contents(get_basecontents(data))
