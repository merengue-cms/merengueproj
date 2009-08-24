# -*- encoding: utf-8 -*-
from django.db.models import Q, get_model
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.geos import LinearRing
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, Template
from django.utils.translation import ugettext

from cmsutils.adminfilters import filter_by_query_string

from merengue.base.models import BaseContent, get_first_model
from merengue.places.forms import SearchFilter
from merengue.section.views import section_view

MIN_FEATURED = 10
MAX_CARRUSEL = 20
CITY_ZOOM = 10


def get_resource_body(destination, resource_model):
    module_name = resource_model._meta.module_name
    return getattr(destination, 'body_%s' % module_name, None)


def places_index(request):
    return section_view(request, 'destinos', {}, 'places/places_index.html')


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


def _get_resources(request, class_name, filters, extra_filter_function=None):
    """Aux function for generic_resource_view and places_ajax_resources_map"""
    if not class_name in settings.CLASS_NAMES_FOR_PLACES:
        raise Http404

    class_names = settings.CLASS_NAMES_FOR_PLACES[class_name]
    extra_or_filter = Q()
    if isinstance(class_names, dict):
        resource_model = get_model(*(class_names.get('resource_model', 'base.basecontent').split('.')))
        for key, value in class_names.get('extra_or_filters', {}).items():
            extra_or_filter = extra_or_filter | Q(**{key: value})
        class_names = class_names.get('class_names', [])
    else:
        resource_model = get_first_model(class_names)
    filters['class_name__in'] = class_names

    contents = resource_model.objects.published().filter(**filters).filter(extra_or_filter).distinct()

    if extra_filter_function is not None:
        contents = extra_filter_function(contents)

    contents, qsm = filter_by_query_string(request, contents,
                                           page_var=settings.PAGE_VARIABLE)
    ordering = resource_model.get_resource_order()
    contents = contents.order_by(*ordering)
    return contents, qsm, resource_model


def generic_resource_view(request, class_name, filters, menuselected,
                          location, extra_filter_function=None,
                          form_filters=None):
    resource_name = ugettext("%s_menu" % class_name)

    contents, qsm, resource_model = _get_resources(request, class_name, filters, extra_filter_function)

    show_searchbar = qsm.search_performed() or contents.count() > settings.SEARCHBAR_MIN_RESULTS

    resource_body = get_resource_body(location, resource_model)

    if form_filters is None:
        form_filters = dict(filters)
        del form_filters['class_name__in']

    form = SearchFilter(data=request.GET, filters=form_filters)
    __recomended_words(form, contents)

    return render_to_response('places/resource_view.html',
                              {'location': location,
                               'location_type': location._meta.verbose_name,
                               'resources': contents,
                               'resource_name': resource_name,
                               'resource_class_name': class_name,
                               'place_type': location._meta.module_name,
                               'menuselected': menuselected,
                               'show_searchbar': show_searchbar,
                               'resource_body': resource_body,
                               'qsm': qsm,
                               'form': form,
                               },
                              context_instance=RequestContext(request))


def content_info(request, content_type, content_id):
    try:
        content = ContentType.objects.get_for_id(content_type)
        content = content.get_object_for_this_type(id=content_id)
        show_single = request.GET.get('show_single', False)
        if isinstance(content, BaseContent) and content.main_location and not show_single:
            # FIXME Tendrá que hacerse con un manager especial
            multiple = [basecontent for basecontent in BaseContent.objects.filter(location__main_location = content.main_location)
                                        if not getattr(basecontent._get_real_instance(), 'resource_owner', None) and
                                           not getattr(basecontent._get_real_instance(), 'content_owner', None)]
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
    # Next line will be used when event app was included
    from merengue.event.models import Event, Occurrence

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
        if ctype.model_class() == Event:
            ctype = ContentType.objects.get_for_model(Occurrence)

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
        contents = [c for c in contents if not getattr(c, 'is_autolocated', False)]
    return render_to_response('base/markers.xml', {'contents': contents,
                                                   'areas': contents,
                                                  },
                                                  context_instance=RequestContext(request))


def __recomended_words(form, contents):
    if form.is_valid():
        form.recommended_other_words(contents)


def places_ajax_resources_map(request, place_type, place_id, class_name):
    model = get_model("places", place_type)
    obj = get_object_or_404(model, id=place_id)

    filters = {}
    resources = _get_resources(request, class_name, filters)
    context = RequestContext(request, {'resources': resources, 'location': obj})

    template = Template("""
    {% load i18n map_tags %}
    <div class="contentMap">
    {% google_map content_pois=resources,content=location %}
    {% if resources|localized %}
    {% google_map_proximity_filter %}
    {% endif %}
    </div>""")

    return HttpResponse(template.render(context))
