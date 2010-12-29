# -*- encoding: utf-8 -*-
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

from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.geos import LinearRing
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

from merengue.base.models import BaseContent


def map_view(request, location, resources,
             template_name='places/map_view.html', display_resources=True,
             menuselected='', extra_context=None, zoom="auto"):
    location_type = location._meta.verbose_name
    context = {'location': location,
               'location_type': location_type,
               'location_type': location_type,
               'menuselected': menuselected,
               'resources': resources,
               'display_resources': display_resources,
               'zoom': zoom}
    if extra_context:
        context.update(extra_context)

    return render_to_response(template_name,
                              context,
                              context_instance=RequestContext(request))


def content_info(request, content_type, content_id):
    try:
        content = ContentType.objects.get_for_id(content_type)
        content = content.get_object_for_this_type(id=content_id)
        show_single = request.GET.get('show_single', False)
        if isinstance(content, BaseContent) and content.main_location and not show_single:
            # FIXME Tendrá que hacerse con un manager especial
            multiple = [basecontent for basecontent in BaseContent.objects.filter(location__main_location = content.main_location)
                                        if not getattr(basecontent.get_real_instance(), 'resource_owner', None) and
                                           not getattr(basecontent.get_real_instance(), 'content_owner', None)]
            extra_contents = len(multiple) > 1
        else:
            multiple = [content]
            extra_contents = False

    except ObjectDoesNotExist:
        raise Http404

    return render_to_response(['%s/%s_content_info.html' % (content._meta.app_label,
                                                            content._meta.module_name),
                               'places/content_info.html'],
                              {'multiple': multiple,
                               'extra_contents': extra_contents,
                              },
                              context_instance=RequestContext(request))


def places_ajax_nearby(request):
    type = request.GET.get('type', None)
    lat1 = request.GET.get('lat1', None)
    lng1 = request.GET.get('lng1', None)
    lat2 = request.GET.get('lat2', None)
    lng2 = request.GET.get('lng2', None)

    contents = []
    if type and lat1 and lng1 and lat2 and lng2:
        lat1 = float(lat1)
        lng1 = float(lng1)
        lat2 = float(lat2)
        lng2 = float(lng2)

        app, model = type.split('.')
        ctype = ContentType.objects.get(app_label=app, model=model)
        rectangle = (
            (lng1, lat1), (lng1, lat2), (lng2, lat2), (lng2, lat1),
            (lng1, lat1),
        )
        bounds = LinearRing(rectangle)

        items = []

        if hasattr(ctype.model_class(), 'location'):
            filter = {'location__main_location__contained': bounds}
        else:
            filter = {'main_location__contained': bounds}
        contents = ctype.model_class().objects.filter(**filter)
    return render_to_response('base/markers.xml', {'contents': contents,
                                                   'areas': contents,
                                                  },
                                                  context_instance=RequestContext(request))
