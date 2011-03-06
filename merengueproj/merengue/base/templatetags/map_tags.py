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

import copy
import hashlib
import os

from django import template
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.template.loader import render_to_string
from django.utils.encoding import smart_str
from django.utils.translation import ugettext as _
from django.utils.translation import get_language

from cmsutils.tag_utils import parse_args_kwargs_and_as_var, \
                               RenderWithArgsAndKwargsNode

if settings.USE_GIS:
    from merengue.base.models import LocatableContent
    from django.contrib.gis.geos import MultiPoint, MultiPolygon


register = template.Library()


if settings.USE_GIS:

    def get_bounds(content, content_pois, content_areas):
        """ gets map bounds. first try to get content bounds,
            last will get content_pois extent """
        points = [c.main_location for c in content_pois if c.has_location()]

        areas = []
        for c in content_areas:
            if hasattr(c, 'location'):
                if getattr(c.location, 'borders', None):
                    areas.append(c.location.borders)
            elif getattr(c, 'borders', None):
                areas.append(c.borders)
        if points and areas:
            mp = MultiPoint(points)
            ap = MultiPolygon(areas)
            return ap.simplify().union(mp).extent
        elif len(points) > 1:
            mp = MultiPoint(points)
            return mp.extent
        elif points:
            # if we have just one point expand the borders
            # to avoid to much zoom
            content = content_pois[0]
        elif areas:
            ap = MultiPolygon(areas)
            return ap.extent
        elif content and content.main_location:
            return (content.main_location.x - 0.002,
                    content.main_location.y - 0.002,
                    content.main_location.x + 0.002,
                    content.main_location.y + 0.002)
        else:
            # default bounding box to avoid google maps failures
            return (settings.DEFAULT_LONGITUDE - 1.0,
                    settings.DEFAULT_LATITUDE - 1.0,
                    settings.DEFAULT_LONGITUDE + 1.0,
                    settings.DEFAULT_LATITUDE + 1.0)

    def write_markers(context, contents, areas, show_area_centroid=False, show_main_image=0):
        xml = render_to_string('base/markers.xml',
                               {'contents': contents,
                                'areas': areas,
                                'show_area_centroid': show_area_centroid,
                                'show_main_image': show_main_image,
                                'MEDIA_URL': context['MEDIA_URL'],
                                'request': context['request']})
        xml_hash = hashlib.md5(smart_str(xml)).hexdigest()
        file_path = 'markers/%s.xml' % xml_hash
        file_fullpath = os.path.join(settings.MEDIA_ROOT, file_path)
        if not os.path.exists(file_fullpath):
            f = open(file_fullpath, 'w')
            f.write(xml.encode('utf-8'))
            f.close()
        return '%s%s' % (settings.MEDIA_URL, file_path)

    def center_bounds(content, bounds):
        if not content.main_location:
            return bounds
        (x0, y0, x1, y1) = bounds
        dx0 = x0 - content.main_location.x
        dy0 = y0 - content.main_location.y
        dx1 = content.main_location.x - x1
        dy1 = content.main_location.y - y1
        if abs(dx0) > abs(dx1):
            x1 = x0 + 2 * abs(dx0)
        else:
            x0 = x1 - 2 * abs(dx1)
        if abs(dy0) > abs(dy1):
            y1 = y0 + 2 * abs(dy0)
        else:
            y0 = y1 - 2 * abs(dy1)
        return (x0, y0, x1, y1)

    class GoogleMapsNode(RenderWithArgsAndKwargsNode):

        def prepare_context(self, args, kwargs, context):
            # variables

            zoom = kwargs.get('zoom', 'auto')

            content_pois = kwargs.get('content_pois', [])
            content = kwargs.get('content', None)

            display_content = kwargs.get('display_content', False)
            display_pois = kwargs.get('display_pois', True)

            content_areas = kwargs.get('content_areas', [])
            show_area_centroid = kwargs.get('show_area_centroid', False)
            show_directions = kwargs.get('show_directions', False)
            travel_directions = kwargs.get('travel_directions', False)
            travel_directions_ajax_url = kwargs.get('travel_directions_ajax_url', '')
            colorify_areas = kwargs.get('colorify_areas', False)
            show_main_image = kwargs.get('show_main_image', False)

            # do stuff
            content_pois = localized(content_pois)

            bounds = None

            if content is None or not content.has_location() or zoom == 'auto':
                zoom_to_bounds = True
                bounds = get_bounds(content, content_pois, content_areas)
                if content and content.has_location():
                    bounds = center_bounds(content, bounds)
            else:
                zoom_to_bounds = False

            if not display_pois:
                content_pois = []  # we calculate bounds, but doesnt show anything

            pois_verbose_name_plural = None
            pois_icon_name = None
            if content_pois or content_areas:
                markers_url = write_markers(context, content_pois,
                                            content_areas, show_area_centroid,
                                            show_main_image)
                if content_pois:
                    first_pois = content_pois[0]
                    if hasattr(first_pois, 'get_real_instance'):
                        first_pois = first_pois.get_real_instance() or first_pois
                    pois_verbose_name_plural = first_pois._meta.verbose_name_plural
                    if hasattr(first_pois, 'get_icon_cluster'):
                        pois_icon_name = first_pois.get_icon_cluster()
                    else:
                        pois_icon_name = '%s_%s_cluster_ico.png' % (first_pois._meta.app_label,
                                                                    first_pois._meta.module_name)
            else:
                markers_url = None

            if content and isinstance(content, LocatableContent) and content.has_location():
                display_content = True
            elif not content:
                display_content = False

            show_map = not context.get('coming_from_buildbot', False)
            # return prepared context for rendering
            return {'show_map': show_map,
                    'content': content,
                    'bounds': bounds,
                    'zoom_to_bounds': zoom_to_bounds,
                    'content_pois': content_pois,
                    'display_content': display_content,
                    'display_pois': display_pois,
                    'content_areas': content_areas,
                    'markers_url': markers_url,
                    'show_directions': show_directions,
                    'travel_directions': travel_directions,
                    'travel_directions_ajax_url': travel_directions_ajax_url,
                    'colorify_areas': colorify_areas,
                    'pois_verbose_name_plural': pois_verbose_name_plural,
                    'pois_icon_name': pois_icon_name,
                    'show_main_image': show_main_image,
                    'MEDIA_URL': context.get('MEDIA_URL', '/media/'),
                    'GOOGLE_MAPS_API_KEY': context.get('GOOGLE_MAPS_API_KEY', ''),
                    'LANGUAGE_CODE': get_language(),
                    'request': context.get('request', None)}

    @register.tag
    def google_map(parser, token):
        args, kwargs, as_var = parse_args_kwargs_and_as_var(parser, token)
        return GoogleMapsNode(args, kwargs, 'base/google_map.html')

    def get_map_type(map_type=None):
        if map_type is None:
            return 'G_NORMAL_MAP'
        else:
            return 'G_%s_MAP' % map_type.upper()

    class GoogleMapsMediaNode(RenderWithArgsAndKwargsNode):

        def prepare_context(self, args, kwargs, context):
            # break this rendering if we are in builbot
            if context.get('coming_from_buildbot', False):
                return {'show_map': False}

            # variables
            content = kwargs.get('content', None)
            map_type = get_map_type(kwargs.get('map_type', None))
            force_cluster = kwargs.get('force_cluster', False)
            on_click = kwargs.get('onclick', None)

            # return prepared context for rendering
            return {'show_map': True,
                    'content': content,
                    'map_type': map_type,
                    'force_cluster': force_cluster,
                    'on_click': on_click,
                    'MEDIA_URL': context.get('MEDIA_URL', '/media/'),
                    'GOOGLE_MAPS_API_KEY': context.get('GOOGLE_MAPS_API_KEY', ''),
                    'LANGUAGE_CODE': get_language(),
                    'request': context.get('request', None)}

    @register.tag
    def google_map_media(parser, token):
        if len(token.split_contents()) == 1:  # No parameters
            args = tuple()
            kwargs = dict()
        else:
            args, kwargs, as_var = parse_args_kwargs_and_as_var(parser, token)
        return GoogleMapsMediaNode(args, kwargs, 'base/google_map_media.html')

    @register.inclusion_tag('base/mini_google_map.html', takes_context=True)
    def mini_google_map(context, content, zoom=4, map_type=None):
        return mini_google_map_with_location(context, content, None, zoom, map_type)

    @register.inclusion_tag('base/mini_google_map.html', takes_context=True)
    def mini_google_map_with_location(context, content, location=None, zoom=4, map_type=None):
        # break this rendering if we are in builbot
        if context.get('coming_from_buildbot', False):
            return {'show_map': False}
        return {
            'show_map': True,
            'content': content,
            'location': location or (content and content.main_location) or None,
            'zoom': zoom,
            'map_type': get_map_type(map_type),
            'MEDIA_URL': context.get('MEDIA_URL', '/media/'),
            }

    def _get_content_types(args):
        if not args:
            args = settings.MAP_FILTRABLE_MODELS
        args = list(args)
        content_types = []
        for arg in args:
            items = arg.replace('"', '').split('.')
            app, model = items[:2]
            type = ContentType.objects.get(app_label=app, model=model)
            type.options = items[2:]
            content_types.append(type)

        return content_types

    class ProximityFilter(template.Node):

        def __init__(self, content_types):
            self.content_types = content_types

        def render(self, context):
            extra_context = copy.copy(context)
            extra_context['content_types'] = self.content_types
            extra_context['filter_title'] = _('What is there nearby?')

            tpl = template.loader.get_template('base/map_filters.html')
            output = tpl.render(extra_context)
            return output

    def google_map_proximity_filter(parser, token):
        try:
            tag_name, args = token.contents.split(None, 1)  # pyflakes:ignore
            args = args.split()
        except ValueError:
            tag_name = token.contents.split()[0]  # pyflakes:ignore
            args = []
        content_types = _get_content_types(args)
        return ProximityFilter(content_types)
    register.tag('google_map_proximity_filter', google_map_proximity_filter)

    def localized(objects):
        return [c for c in objects
                if (getattr(c, 'has_location', None)
                    and c.has_location())]

    register.filter('localized', localized)
else:

    class dummyNode(template.Node):

        def render(self, *args, **kwargs):
            return ''

    def dummy_tag(*args):
        return dummyNode()

    def dummy_filter(value, *args):
        return ''

    register.tag('mini_google_map', dummy_tag)
    register.tag('mini_google_map_with_location', dummy_tag)
    register.tag('google_map_media', dummy_tag)
    register.tag('google_map', dummy_tag)
    register.tag('google_map_proximity_filter', dummy_tag)
    register.filter('localized', dummy_filter)
