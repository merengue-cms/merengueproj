from django.conf import settings
from django.contrib.gis import admin as geoadmin
from django.contrib.gis.maps.google import GoogleMap

from transmeta import canonical_fieldname
from merengue.base.admin import BaseAdmin


GMAP = GoogleMap(key=settings.GOOGLE_MAPS_API_KEY)


class GoogleAdmin(geoadmin.OSMGeoAdmin, BaseAdmin):
    extra_js = [GMAP.api_url + GMAP.key]
    map_width = 500
    map_height = 300
    default_zoom = 10
    default_lat = 4500612.0
    default_lon = -655523.0
    map_template = 'gis/admin/google.html'


def comes_from_buildbot(request):
    if hasattr(settings, 'BUILDBOT_IP'):
        if request.META.get('REMOTE_ADDR') == settings.BUILDBOT_IP:
            return True
    return False


class BasePlaceAdmin(BaseAdmin):

    def formfield_for_dbfield(self, db_field, **kwargs):
        field = super(BasePlaceAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        db_fieldname = canonical_fieldname(db_field)
        if db_fieldname == 'description':
            field.widget.attrs['rows'] = 4
        return field
