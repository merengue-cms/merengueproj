# -*- encoding: utf-8 -*-
from django.db.models import Q, get_model
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.geos import LinearRing
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, Template
from django.utils import simplejson
from django.utils.translation import ugettext

from cmsutils.adminfilters import filter_by_query_string
from cmsutils.decorators import i18ncache_page

from base.decorators import content_public_required
from base.models import BaseContent, get_first_model
from base.views import search_results
from places.forms import (PlacesQuickSearchForm,
                          PlacesAdvancedSearchForm,
                          ProvinceResourcesQuickSearchForm,
                          ProvinceResourcesAdvancedSearchForm,
                          TouristZoneResourcesQuickSearchForm,
                          TouristZoneResourcesAdvancedSearchForm)
from places.models import BaseCity, Village, City, Province, TouristZone
from places.forms import SearchFilter
from multimedia.models import Video, Photo, Image3D, PanoramicView
from event.models import Event, Occurrence
from searchform.utils import search_button_submitted
from section.views import section_view

import random

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


def _get_resources(request, class_name, filters, extra_filter_function):
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

    form = SearchFilter(data=request.GET, show_city_field=True, filters=form_filters)
    __recomended_words(form, contents)

    return render_to_response('places/resource_view.html',
                              {'location': location,
                               'location_type': location._meta.verbose_name,
                               'resources': contents,
                               'resource_name': resource_name,
                               'resource_class_name': class_name,
                               'place_type': location._meta.module_name,
                               'menuselected': menuselected,
                               'show_city_field': True,
                               'show_searchbar': show_searchbar,
                               'resource_body': resource_body,
                               'qsm': qsm,
                               'form': form,
                               },
                              context_instance=RequestContext(request))



## PROVINCE VIEWS ##


@content_public_required(slug_field='province_slug', model=Province)
def province_view(request, province_slug):
    province = get_object_or_404(Province, slug=province_slug)
    location_type = province._meta.verbose_name
    tzones = TouristZone.objects.filter(province=province)
    filter = dict(location__cities__province=province)
    carousel_contents = BaseContent.objects.filter(**filter)
    return render_to_response('places/province_view.html',
                              {'location': province,
                               'location_type': location_type,
                               'tzones': tzones,
                               'carousel_contents': carousel_contents},
                              context_instance=RequestContext(request))


def province_map_view(request, province_slug):
    province = get_object_or_404(Province, slug=province_slug)
    contents = province.basecity_set.published()
    return map_view(request, province, contents, menuselected='province-%s' % province.slug)


def province_search_view(request, province_slug):
    return HttpResponseRedirect(reverse('province_quick_search',
                                        args=[province_slug]))


def _internal_province_search(request, form_class, province_slug):
    province = get_object_or_404(Province, slug=province_slug)
    search_form = form_class()
    search_form.bind_to_province(province)

    if search_button_submitted(request):
        return search_results(request, search_form)
    else:
        kwargs = {'args': [province_slug]}
        context = {
            'quick_search_url': reverse('province_quick_search', **kwargs),
            'advanced_search_url': reverse('province_advanced_search', **kwargs),
            'search_form': search_form,
            'content': province,
            'menuselected': search_form.get_selected_menu(),
            }
        return render_to_response('places/places_search.html',
                                  context,
                                  context_instance=RequestContext(request))


def province_quick_search(request, province_slug):
    return _internal_province_search(request, ProvinceResourcesQuickSearchForm, province_slug)


def province_advanced_search(request, province_slug):
    return _internal_province_search(request, ProvinceResourcesAdvancedSearchForm, province_slug)


def _province_resource_filters(province, class_name):
    """Aux function for province_resource_view and places_ajax_resources_map"""
    return {'location__cities__province': province}, None


def province_resource_view(request, province_slug, class_name):
    province = get_object_or_404(Province, slug=province_slug)
    filter = _province_resource_filters(province, class_name)[0]
    menuselected = 'province-%s' % province.slug
    return generic_resource_view(request, class_name, filter, menuselected, province)


def province_cities(request, province_slug):
    province = get_object_or_404(Province, slug=province_slug)
    location_type = province._meta.verbose_name

    resource_type = ContentType.objects.get_for_model(City)
    resource_model = resource_type.model_class()
    resource_name = ugettext("%s_menu" % resource_model._meta.module_name)
    contents = BaseCity.objects.published().filter(province=province)

    contents, qsm = filter_by_query_string(request, contents,
                                           page_var=settings.PAGE_VARIABLE)

    show_searchbar = qsm.search_performed() or contents.count() > settings.SEARCHBAR_MIN_RESULTS
    menuselected = 'province-%s' % province.slug

    resource_body = get_resource_body(province, resource_model)
    form = SearchFilter(data=request.GET, filters={'location__cities__province': province})
    __recomended_words(form, contents)
    return render_to_response('places/city_resource_view.html',
                              {'location': province,
                               'location_type': location_type,
                               'resources': contents,
                               'resource_name': resource_name,
                               'menuselected': menuselected,
                               'show_searchbar': show_searchbar,
                               'resource_body': resource_body,
                               'qsm': qsm,
                               'form': form,
                               },
                              context_instance=RequestContext(request))


def city_villages(request, province_slug, city_slug):
    city = get_object_or_404(City, slug=city_slug)
    province = get_object_or_404(Province, slug=province_slug)
    location_type = city._meta.verbose_name

    resource_type = ContentType.objects.get_for_model(Village)
    resource_model = resource_type.model_class()
    resource_name = ugettext("%s_menu" % resource_model._meta.module_name)

    contents = city.villages.published()

    contents, qsm = filter_by_query_string(request, contents,
                                           page_var=settings.PAGE_VARIABLE)
    show_searchbar = qsm.search_performed() or contents.count() > settings.SEARCHBAR_MIN_RESULTS

    menuselected = 'province-%s' % province.slug

    for zone in city.touristzone.all():
        menuselected += ' touristzone-%s' % zone.slug

    resource_body = get_resource_body(city, Village)

    form = SearchFilter(data=request.GET, filters={'location__cities__province': province, \
                                                   'location__cities__city': city})
    __recomended_words(form, contents)
    return render_to_response('places/city_resource_view.html',
                              {'location': city,
                               'location_type': location_type,
                               'resources': contents,
                               'resource_name': resource_name,
                               'menuselected': menuselected,
                               'show_searchbar': show_searchbar,
                               'resource_body': resource_body,
                               'qsm': qsm,
                               'form': form,
                               },
                              context_instance=RequestContext(request))


def province_multimedia(request, province_slug):
    province = get_object_or_404(Province, slug=province_slug)
    return destination_multimedia(request, province)




## TOURIST ZONE VIEWS ##


@content_public_required(slug_field='touristzone_slug', model=TouristZone)
def touristzone_view(request, touristzone_slug):
    touristzone = get_object_or_404(TouristZone, slug=touristzone_slug)
    location_type = touristzone._meta.verbose_name
    filter = dict(location__cities__touristzone=touristzone)
    contents = BaseContent.objects.filter(**filter)
    has_information = (touristzone.body
                       or touristzone.body_history
                       or touristzone.body_restaurant)
    return render_to_response('places/touristzone_view.html',
                              {'location': touristzone,
                               'location_type': location_type,
                               'has_information': has_information,
                               'resources': contents},
                              context_instance=RequestContext(request))


def touristzone_map_view(request, touristzone_slug):
    touristzone = get_object_or_404(TouristZone, slug=touristzone_slug)
    contents = touristzone.cities.published()
    menuselected='province-%s touristzone-%s' % (touristzone.province.slug, touristzone.slug)
    return map_view(request, touristzone, contents, menuselected=menuselected)


def _touristzone_resource_filters(touristzone, class_name):
    """Aux function for touristzone_resource_view and places_ajax_resources_map"""
    return {'location__cities__touristzone': touristzone}, None


def touristzone_resource_view(request, touristzone_slug, class_name):
    touristzone = get_object_or_404(TouristZone, slug=touristzone_slug)
    filter = _touristzone_resource_filters(touristzone, class_name)[0]
    menuselected = 'province-%s touristzone-%s' % (touristzone.province.slug, touristzone.slug)
    return generic_resource_view(request, class_name, filter, menuselected, touristzone)


def touristzone_search_view(request, touristzone_slug):
    return HttpResponseRedirect(reverse('touristzone_quick_search',
                                        args=[touristzone_slug]))


def _internal_touristzone_search(request, form_class, touristzone_slug):
    touristzone = get_object_or_404(TouristZone, slug=touristzone_slug)
    search_form = form_class()
    search_form.bind_to_touristzone(touristzone)
    if search_button_submitted(request):
        return search_results(request, search_form)
    else:
        kwargs = {'args': [touristzone_slug]}
        context = {
            'quick_search_url': reverse('touristzone_quick_search', **kwargs),
            'advanced_search_url': reverse('touristzone_advanced_search', **kwargs),
            'search_form': search_form,
            'content': touristzone,
            'menuselected': search_form.get_selected_menu(),
            }
        return render_to_response('places/places_search.html',
                                  context,
                                  context_instance=RequestContext(request))


def touristzone_quick_search(request, touristzone_slug):
    return _internal_touristzone_search(request,
                                        TouristZoneResourcesQuickSearchForm,
                                        touristzone_slug)


def touristzone_advanced_search(request, touristzone_slug):
    return _internal_touristzone_search(request,
                                        TouristZoneResourcesAdvancedSearchForm,
                                        touristzone_slug)


def touristzone_cities(request, touristzone_slug):
    touristzone = get_object_or_404(TouristZone, slug=touristzone_slug)
    location_type = touristzone._meta.verbose_name
    resource_type = ContentType.objects.get_for_model(City)
    resource_model = resource_type.model_class()
    resource_name = ugettext("%s_menu" % resource_model._meta.module_name)
    contents = touristzone.cities.published()

    contents, qsm = filter_by_query_string(request, contents,
                                           page_var=settings.PAGE_VARIABLE)
    show_searchbar = qsm.search_performed() or contents.count() > settings.SEARCHBAR_MIN_RESULTS
    menuselected='province-%s touristzone-%s' % (touristzone.province.slug, touristzone.slug)
    form = SearchFilter(data=request.GET, filters={'location__cities__touristzone': touristzone})
    __recomended_words(form, contents)
    return render_to_response('places/city_resource_view.html',
                              {'location': touristzone,
                               'location_type': location_type,
                               'resources': contents,
                               'resource_name': resource_name,
                               'menuselected': menuselected,
                               'show_searchbar': show_searchbar,
                               'qsm': qsm,
                               'form': form,
                               },
                              context_instance=RequestContext(request))


def touristzone_multimedia(request, touristzone_slug):
    touristzone = get_object_or_404(TouristZone, slug=touristzone_slug)
    return destination_multimedia(request, touristzone)


## CITY VIEWS ##


@content_public_required(slug_field='city_slug', model=BaseCity)
def city_view(request, province_slug, city_slug):
    basecity = get_object_or_404(BaseCity, slug=city_slug)
    province = get_object_or_404(Province, slug=province_slug)
    city = basecity._get_real_instance()
    location_type = city._meta.verbose_name
    filter = dict(location__cities=city)
    contents = BaseContent.objects.filter(**filter)
    has_information = (city.body
                       or city.body_history
                       or city.body_restaurant)
    menuselected = 'province-%s' % city.province.slug
    for zone in city.touristzone.all():
        menuselected += ' touristzone-%s' % zone.slug

    return render_to_response('places/city_view.html',
                              {'location': city,
                               'location_type': location_type,
                               'resources': contents,
                               'menuselected': menuselected,
                               'has_information': has_information},
                              context_instance=RequestContext(request))


def city_map_view(request, province_slug, city_slug):
    basecity = get_object_or_404(BaseCity, slug=city_slug)
    province = get_object_or_404(Province, slug=province_slug)
    city = basecity._get_real_instance()
    contents = BaseContent.objects.filter(location__cities=city).select_related('location')
    menuselected = 'province-%s' % city.province.slug
    for zone in city.touristzone.all():
        menuselected += ' touristzone-%s' % zone.slug
    return map_view(request, city, contents, menuselected=menuselected, display_resources=False, zoom=CITY_ZOOM)


def _city_resource_filters(city, class_name):
    """Aux function for city_resource_view and places_ajax_resources_map"""
    province = city.province

    def filter_cities_or_villages(queryset):
        city_filters = dict(location__cities=city)
        villages_filters = isinstance(city, City) and dict(location__cities__in=city.villages.all()) or {}
        return queryset.filter(Q(**city_filters) | Q(**villages_filters)).distinct()

    return {}, filter_cities_or_villages


def city_resource_view(request, province_slug, city_slug, class_name):
    basecity = get_object_or_404(BaseCity, slug=city_slug)
    province = get_object_or_404(Province, slug=province_slug)
    city = basecity._get_real_instance()
    province = city.province

    menuselected = 'province-%s' % city.province.slug
    for zone in city.touristzone.all():
        menuselected += ' touristzone-%s' % zone.slug

    form_filters = {'location__cities__province': province,
                    'location__cities__city': basecity}
    filters, extra_filter_function = _city_resource_filters(city, class_name)
    return generic_resource_view(request, class_name, filters, menuselected, city,
                                 extra_filter_function=extra_filter_function,
                                 form_filters=form_filters)


def city_multimedia(request, province_slug, city_slug):
    city = get_object_or_404(BaseCity, slug=city_slug)
    province = get_object_or_404(Province, slug=province_slug)
    return destination_multimedia(request, city)


def city_history(request, province_slug, city_slug):
    city = get_object_or_404(BaseCity, slug=city_slug)
    province = get_object_or_404(Province, slug=province_slug)
    return destination_history(request, city)


## SEARCH VIEWS ##


def places_search(request):
    return HttpResponseRedirect(reverse('places_quick_search'))


def _internal_places_search(request, form_class):
    search_form = form_class()
    if search_button_submitted(request):
        return search_results(request, search_form)
    else:
        context = {
            'quick_search_url': reverse('places_quick_search'),
            'advanced_search_url': reverse('places_advanced_search'),
            'content': None,
            'search_form': form_class(),
            'menuselected': search_form.get_selected_menu(),
            'cities': BaseCity.objects.published(),
            }
        return render_to_response('places/places_search.html',
                                  context,
                                  context_instance=RequestContext(request))


def places_quick_search(request):
    return _internal_places_search(request, PlacesQuickSearchForm)


def places_advanced_search(request):
    return _internal_places_search(request, PlacesAdvancedSearchForm)


@i18ncache_page(cache_query_string=True)
def places_ajax_province_coast(request):
    return places_ajax_province(request, {'province__coast__isnull': False, 'location__basecontent__class_name': 'beach'})


@i18ncache_page(cache_query_string=True)
def places_ajax_province(request, filters={}):
    province_id = request.GET.get('provincia_id', None)
    class_name = request.GET.get('class_name', None)
    qfilter=Q()
    if class_name and class_name == 'deal':
        qfilter = (Q(location__basecontent__class_name = class_name) |
                   Q(location__basecontent__offer__isnull=False))
    elif class_name and class_name == 'transport': # FIXME
        from directions.models import BaseTransport
        qfilter = (Q(location__basecontent__class_name__in = [
                        item['class_name'] for item in
                            BaseTransport.objects.all().distinct('class_name').values('class_name').order_by('class_name')]))
    elif class_name and class_name == 'convention': # FIXME
        from convention.models import BaseConvention
        qfilter = (Q(location__basecontent__class_name__in = [
                        item['class_name'] for item in
                            BaseConvention.objects.all().distinct('class_name').values('class_name').order_by('class_name')]))
    elif class_name:
        filters.update({'location__basecontent__class_name': class_name})
    if province_id is None:
        cities = list(BaseCity.objects.published().filter(**filters).filter(qfilter).distinct().values('id', 'name'))
        tourist_zones = list(TouristZone.objects.published().values('id', 'name'))
    else:
        province = get_object_or_404(Province, id=int(province_id))
        cities = list(province.basecity_set.published().filter(**filters).filter(qfilter).distinct().values('id', 'name'))
        tourist_zones = list(province.touristzone_set.published().values('id', 'name'))

    data = {'cities': cities, 'tourist_zones': tourist_zones}
    json = simplejson.dumps(data, ensure_ascii=False)
    return HttpResponse(json, 'text/javascript')


@i18ncache_page(cache_query_string=True)
def places_ajax_tourist_zone(request, filters={}):
    tourist_zone_id = request.GET.get('zona_turistica_id', None)
    class_name = request.GET.get('class_name', None)
    if class_name:
        filters.update({'location__basecontent__class_name': class_name})
    if tourist_zone_id is None:
        cities = list(BaseCity.objects.published().filter(**filters).distinct().values('id', 'name'))
        province = None
    else:
        tourist_zone = get_object_or_404(TouristZone, id=int(tourist_zone_id))
        cities = list(tourist_zone.cities.published().filter(**filters).distinct().values('id', 'name'))
        province = {'id': tourist_zone.province.id,
                    'name': tourist_zone.province.name}

    data = {'cities': cities, 'province': province}
    json = simplejson.dumps(data, ensure_ascii=False)
    return HttpResponse(json, 'text/javascript')


@i18ncache_page(cache_query_string=True)
def places_ajax_city(request):
    city_id = request.GET.get('municipio_id', None)
    tourist_zones = None
    province = None
    if city_id is None or not city_id.isdigit():
        tourist_zones = list(TouristZone.objects.published().values('id', 'name'))
    else:
        city = get_object_or_404(BaseCity, id=int(city_id))
        tourist_zones = list(city.touristzone.published().values('id', 'name'))
        province = {'id': city.province.id,
                    'name': city.province.name}

    data = {'tourist_zones': tourist_zones, 'province': province}
    json = simplejson.dumps(data, ensure_ascii=False)
    return HttpResponse(json, 'text/javascript')


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


def places_ajax_related(request):
    type = request.GET.get('type', None)
    related_type = request.GET.get('related_type', None)
    related_id = request.GET.get('related_id', None)

    contents = []
    if type and related_type and related_id:
        object = ContentType.objects.get_for_id(related_type).get_object_for_this_type(id=related_id)

        app, model = type.split('.')
        ctype = ContentType.objects.get(app_label=app, model=model)
        if ctype.model_class() == Event:
            ctype = ContentType.objects.get_for_model(Occurrence)

        items = []

        if isinstance(object, BaseCity):
            filter = {'location__cities': object}
        elif isinstance(object, Province):
            filter = {'location__cities__province': object}
        elif isinstance(object, TouristZone):
            filter = {'location__cities__in': object.cities.published()}
        else:
            filter = {}
        filter.update({'location__main_location__isnull': False})
        contents = ctype.model_class().objects.filter(**filter)
        contents = [c for c in contents if not getattr(c, 'is_autolocated', False)]
    return render_to_response('base/markers.xml', {'contents': contents,
                                                   'areas': contents,
                                                  },
                                                  context_instance=RequestContext(request))


def destination_multimedia(request, location, extra_context={}):
    location_type = location._meta.module_name


    filter_photos = None
    more_destinations_filter = Q()

    if isinstance(location, BaseCity):
        filter = {'location__cities': location}
        menu_items = ['province-%s' % location.province.slug]
        for zone in location.touristzone.published():
            menu_items.append('touristzone-%s' % zone.slug)
        menuselected = ' '.join(menu_items)
        if location.class_name == 'city':
            villages = location.city.villages.published()
            filter_photos = {'location__cities__in': villages}
            more_destinations_filter = Q(basecity__in=villages)
    elif isinstance(location, Province):
        filter = {'location__cities__province': location}
        menuselected = 'province-%s' % location.slug
        more_destinations_filter = Q(basecity__in=location.basecity_set.published())|\
                                   Q(touristzone__in=location.touristzone_set.published())
    elif isinstance(location, TouristZone):
        filter = {'location__cities__in': location.cities.published()}
        menuselected = 'province-%s touristzone-%s' % (location.province.slug,
                                                        location.slug)
        more_destinations_filter = Q(basecity__in=location.cities.published())
    else:
        filter = {}
        menuselected = ''

    content_ids = BaseContent.objects.filter(**filter).values('id').query
    if filter_photos:
        content_ids_photos = BaseContent.objects.filter(Q(**filter) | Q(**filter_photos)).values('id').query
    else:
        content_ids_photos = content_ids

    location_videos = location.multimedia.videos().published()
    location_photos = location.multimedia.photos().published()
    location_image3d = location.multimedia.images3d().published()
    location_panoramicview = location.multimedia.panoramic_views().published()

    contents = []
    contents.append(Video.objects.published().filter(Q(basecontent__in=content_ids)|more_destinations_filter).distinct())
    contents.append(Photo.objects.published().filter(Q(basecontent__in=content_ids_photos)|more_destinations_filter).distinct())
    contents.append(Image3D.objects.published().filter(Q(basecontent__in=content_ids)|more_destinations_filter))
    contents.append(PanoramicView.objects.published().filter(Q(basecontent__in=content_ids)|more_destinations_filter))

    res = []
    for content in contents:
        featured = content.filter(multimediarelation__is_featured=True)
        if featured.count() >= MIN_FEATURED:
            content = featured
        if content.count() > MAX_CARRUSEL:
            content = list(content)[:MAX_CARRUSEL]
            random.shuffle(content)
        res.append(content)
    return render_to_response('places/places_multimedia.html',
                              {'location': location,
                               'location_type': location_type,
                               'menuselected': menuselected,
                               'location_videos': location_videos,
                               'content_videos': res[0],
                               'location_photos': location_photos,
                               'content_photos': res[1],
                               'location_image3d': location_image3d,
                               'content_image3d': res[2],
                               'location_panoramicview': location_panoramicview,
                               'content_panoramicview': res[3],
                              },
                              context_instance=RequestContext(request))


def destination_history(request, location, extra_context={}):
    location_type = location._meta.verbose_name
    carousel_contents = BaseContent.objects.filter(location__cities=location)
    menuselected = 'province-%s' % location.province.slug
    for zone in location.touristzone.all():
        menuselected += ' touristzone-%s' % zone.slug
    return render_to_response('places/places_history.html',
                              {'location': location,
                               'location_type': location_type,
                               'carousel_contents': carousel_contents,
                               'menuselected': menuselected,
                              },
                              context_instance=RequestContext(request))


def location_redirect(request, plone_uid, location_model='city'):
    """ Redirect to city or province view from plone_uid of content """
    obj = get_object_or_404(BaseContent, plone_uid=plone_uid)
    cities = obj.location.cities.all()
    if not cities:
        raise Http404
    if location_model == 'city':
        url = cities.filter(class_name='city')[0].get_absolute_url()
    elif location_model == 'village':
        url = cities.filter(class_name='village')[0].get_absolute_url()
    elif location_model == 'province':
        url = cities[0].province.get_absolute_url()
    else:
        raise Http404
    return HttpResponseRedirect(url)


def __recomended_words(form, contents):
    if form.is_valid():
        form.recommended_other_words(contents)


def places_ajax_resources_map(request, place_type, place_id, class_name):
    model = get_model("places", place_type)
    obj = get_object_or_404(model, id=place_id)
    resources_generators = {
        'city': _city_resource_filters,
        'touristzone': _touristzone_resource_filters,
        'province': _province_resource_filters,
        }
    if place_type not in resources_generators:
        raise Http404

    filters, extra_filter_function = resources_generators[place_type](obj, class_name)
    resources = _get_resources(request, class_name, filters, extra_filter_function)[0]
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
