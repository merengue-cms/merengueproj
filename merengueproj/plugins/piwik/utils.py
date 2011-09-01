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


def get_pagetitle_stats(expanded=1):
    piwik_api = get_piwik_api()
    site_id = get_site_id()
    period = get_period()
    date = get_date()
    data = piwik_api.call('Actions.getPageTitles', params={'idSite': site_id,
                                                           'period': period,
                                                           'date': date,
                                                           'filter_pattern_recursive': 'id:',
                                                           'filter_column_recursive': 'label',
                                                           'expanded': expanded}, format='json')
    return data


def get_basecontents_from_customvariables(data=None):
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


def get_basecontents(data, extra_filters=None):
    pattern = ".*id:(\d+).*"
    contents = {}
    metric = get_metric()
    for entry in data:
        match = re.match(pattern, entry['label'])
        id = None
        if match:
            id = match.groups()[0]
        if id:
            filters = {'id': id}
            if extra_filters:
                filters.update(extra_filters)
            try:
                content = BaseContent.objects.get(**filters)
            except BaseContent.DoesNotExist:
                continue

            if not content in contents:
                contents[content] = {}
            contents[content]['visits'] = contents[content].get('visits', 0) + entry.get(metric, 0)
            if 'subtable' in entry:
                children = get_basecontents(entry['subtable'])
                if contents[content].get('children', None):
                    for child, child_metric in children.iteritems():
                        if child in contents[content]['children']:
                            contents[content]['children'][child]['visits'] += child_metric['visits']
                        else:
                            contents[content]['children'].update(child)
                else:
                    contents[content]['children'] = children

    return contents


def sort_contents(contents):
    return sorted(contents.iteritems(), key=lambda k: k[1]['visits'], reverse=True)


def sort_contents_recursive(contents):
    for content, data in contents.iteritems():
        if 'children' in data:
            data['children'] = sort_contents_recursive(data['children'])
    return sort_contents(contents)


def get_contents_from_customvariables():
    data = get_variable_stats(CONTENT_PIWIK_VARIABLE)
    return sort_contents(get_basecontents_from_customvariables(data))


def get_sections_from_customvariables():
    data = get_variable_stats(SECTION_PIWIK_VARIABLE)
    return sort_contents(get_basecontents_from_customvariables(data))


def get_contents(username=None, expanded=1):
    base_contents = None
    data = get_pagetitle_stats(expanded)
    if data:
        if username:
            filters = {'owners__username': username}
            base_contents = get_basecontents(data, filters)
        else:
            base_contents = get_basecontents(data)
        if base_contents:
            return sort_contents_recursive(base_contents)
    return []
