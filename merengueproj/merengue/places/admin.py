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
