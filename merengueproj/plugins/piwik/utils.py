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

from merengue.base.models import BaseContent
from merengue.pluggable.utils import get_plugin

from plugins.piwik.api import PiwikAPI
from plugins.piwik.settings import METRIC

_piwik_api = None


def get_piwik_api(reload=True):
    global _piwik_api
    if _piwik_api is None or reload:
        _piwik_api = PiwikAPI()
    return _piwik_api


def get_basecontents(data, extra_filters=None):
    pattern = ".*id:(\d+).*"
    contents = {}
    metric = get_plugin('piwik').get_config().get('metric').get_value() or METRIC
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
                            contents[content]['children'].update({child: {'visits': child_metric['visits']}})
                else:
                    contents[content]['children'] = children

    return contents


def get_contents(user=None, expanded=1):
    base_contents = None
    piwik_api = get_piwik_api()
    data = piwik_api.call('Actions.getPageTitles',
                  params={'filter_pattern_recursive': 'id:',
                          'filter_column_recursive': 'label',
                          'expanded': expanded})
    if data and isinstance(data, list):
        if user:
            if user.is_authenticated():
                filters = {'owners': user}
                base_contents = get_basecontents(data, filters)
            else:
                base_contents = {}
        else:
            base_contents = get_basecontents(data)
        if base_contents is not None:
            return sort_contents_recursive(base_contents)
    elif data and isinstance(data, dict):
        return data
    return data


def sort_contents(contents):
    return sorted(contents.iteritems(), key=lambda k: k[1]['visits'], reverse=True)


def sort_contents_recursive(contents):
    for content, data in contents.iteritems():
        if 'children' in data:
            data['children'] = sort_contents_recursive(data['children'])
    return sort_contents(contents)
