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


@register.inclusion_tag('base/search_results.html', takes_context=True)
def search_results(context, result_list, with_rating=False):
    return {'result_list': result_list,
            'request': context.get('request', None),
            'MEDIA_URL': context.get('MEDIA_URL', '/media/'),
            'LANGUAGE_CODE': context.get('LANGUAGE_CODE', 'es'),
            'GOOGLE_MAPS_API_KEY': context.get('GOOGLE_MAPS_API_KEY', ''),
            'user': context['user'],
            'with_rating': with_rating,
            }
