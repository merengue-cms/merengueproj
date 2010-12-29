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

register = template.Library()


@register.inclusion_tag('event/range_dates.html', takes_context=True)
def range_dates(context, start, end):
    if end == start:
        end = None
    return {'start': start,
            'end': end,
            'request': context.get('request')}


@register.inclusion_tag('event/range_dates_as_tag.html', takes_context=True)
def range_dates_as_tag(context, start, end, tag='span', classdef=None):
    if end == start:
        end = None
    return {'start': start,
            'end': end,
            'classdef': classdef,
            'tag': tag,
            'request': context.get('request')}
