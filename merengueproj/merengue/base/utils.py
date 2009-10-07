from django.conf import settings
from django.core.cache import cache
from django.utils.cache import _generate_cache_header_key
from django.utils.encoding import smart_str
from geopy import geocoders

from merengue.base.models import Location


def geolocate_object_base(object_base_content):
    if not object_base_content.location:
        object_base_content.location=Location.objects.create()
    city = object_base_content.location.cities.all()
    city = (city and city[0]) or ""
    address = object_base_content.location.address or ""
    number = object_base_content.location.number or ""
    postal_code = object_base_content.location.postal_code or ""
    address_type = ""
    if object_base_content.location.address_type_id and object_base_content.location.address_type.name != 'Otros':
        address_type = object_base_content.location.address_type.name or ""

    query = u"%s %s %s %s %s, andalusia, spain" % (address_type, address, number, postal_code, city)
    query = smart_str(query.strip())
    g = geocoders.Google(settings.GOOGLE_MAPS_API_KEY, 'maps.google.es')
    try:
        place_google, (lat, lon) = g.geocode(query)
        object_base_content.location.main_location = 'POINT(%f %f)' % (lon, lat)
        object_base_content.location.save()
        object_base_content.is_autolocated = True
        object_base_content.save()
    except ValueError, e:
        pass


def copy_request(request, delete_list):
    from copy import deepcopy
    request_copy = deepcopy(request)
    for delete_item in delete_list:
        if delete_item in request_copy.GET:
            del request_copy.GET[delete_item]
    return request_copy


def invalidate_cache_for_path(request_path):
    """ invalidates cache based on request.path """
    # wrap a dummy request object for call django function
    request = object()
    request.path = request_path
    cache_header_key = _generate_cache_header_key(settings.CACHE_MIDDLEWARE_KEY_PREFIX, request)
    cache.delete(cache_header_key)
