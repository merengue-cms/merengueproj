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

from transmeta import get_fallback_fieldname

from merengue.base.admin import BaseContentAdmin, BaseCategoryAdmin
from merengue.section.admin import SectionContentAdmin
from plugins.event.models import Event, Category


class EventCategoryAdmin(BaseCategoryAdmin):
    ordering = (get_fallback_fieldname('name'), )
    search_fields = (get_fallback_fieldname('name'), )


class EventAdmin(BaseContentAdmin):
    ordering = (get_fallback_fieldname('name'), )
    search_fields = ('name', )
    exclude = ('expire_date', )
    list_display = ('name', 'start', 'end', 'status', 'user_modification_date',
                    'last_editor')
    if settings.USE_GIS:
        list_display = list_display + ('google_minimap', )
    list_filter = ('categories', 'status', 'user_modification_date', )


class EventSectionAdmin(EventAdmin, SectionContentAdmin):
    manage_contents = True


def register(site):
    site.register(Category, EventCategoryAdmin)
    site.register(Event, EventAdmin)
