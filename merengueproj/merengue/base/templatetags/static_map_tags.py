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

from cmsutils.tag_utils import parse_args_kwargs_and_as_var, \
                               RenderWithArgsAndKwargsNode


register = template.Library()


def get_latitude_longitude(content, latitude=None, longitude=None, att_location=['main_location']):
    if getattr(content, 'has_location', None) and content.has_location() and (not latitude or not longitude):
        if getattr(content, 'get_location', None):
            content = content.get_location()
        elif getattr(content, 'location', None):
            content = content.location
        for att in att_location:
            if getattr(content, att, None):
                latitude = getattr(content, att).y
                longitude = getattr(content, att).x
                if latitude and longitude:
                    break
    return latitude, longitude


class StaticMapUtil(object):
    pass


class StaticMapNode(RenderWithArgsAndKwargsNode, StaticMapUtil):

    def prepare_context(self, args, kwargs, context):
        content = kwargs.get('content', None)
        latitude = kwargs.get('latitude', None)
        longitude = kwargs.get('longitude', None)
        zoom = kwargs.get('zoom', 12)
        height = kwargs.get('height', 300)
        width = kwargs.get('width', 300)
        latitude, longitude = get_latitude_longitude(content, latitude, longitude)
        return {'latitude': latitude,
                'longitude': longitude,
                'zoom': zoom,
                'height': height,
                'width': width,
                'GOOGLE_MAPS_API_KEY': context.get('GOOGLE_MAPS_API_KEY', ''),
                }


@register.tag
def static_map(parser, token):
    args, kwargs, as_var = parse_args_kwargs_and_as_var(parser, token)
    return StaticMapNode(args, kwargs, 'base/google_static_map.html')


class StaticMapRouteNode(RenderWithArgsAndKwargsNode, StaticMapUtil):

    def prepare_context(self, args, kwargs, context):
        contents = kwargs.get('contents', [])
        color_route = kwargs.get('color_route', '0xff0000ff')
        weight = kwargs.get('weight', 3)
        height = kwargs.get('height', 400)
        width = kwargs.get('width', 400)
        contents_len = len(contents)
        contents_route = []
        colors_google = ['black', 'brown', 'green', 'purple', 'yellow', 'blue', 'gray', 'orange', 'red', 'white']
        colors_converter = {'black': '#626262', 'brown': '#b98410', 'green': '#62b346',
                            'purple': '#9571fb', 'yellow': '#faf156', 'blue': '#43aafe',
                            'gray': '#bcbcbb', 'orange': '#fea800', 'red': '#62b346', 'white': '#fdfdfc'}
        markers = ''
        path = ''
        first_letter = ord('a')
        last_letter = ord('z')
        i = 0
        for content in contents:
            latitude, longitude = get_latitude_longitude(content)
            if latitude and longitude:
                content_route = {}
                content_route['content'] = content
                content_route['latitude'] = latitude
                content_route['longitude'] = longitude
                color_google = colors_google[i%len(colors_google)]
                content_route['color'] = colors_converter[color_google]
                content_route['letter'] = chr((i+first_letter)%last_letter)
                markers += '%s,%s,%s%s|' %(latitude, longitude, color_google, content_route['letter'])
                path += '%s,%s|' %(latitude, longitude)
                contents_route.append(content_route)
                i += 1
        return {'markers': markers,
                'path': path,
                'height': height,
                'width': width,
                'weight': weight,
                'contents_route': contents_route,
                'color_route': color_route,
                'GOOGLE_MAPS_API_KEY': context.get('GOOGLE_MAPS_API_KEY', ''),
                }


@register.tag
def static_map_route(parser, token):
    args, kwargs, as_var = parse_args_kwargs_and_as_var(parser, token)
    return StaticMapRouteNode(args, kwargs, 'base/google_static_map_route.html')
