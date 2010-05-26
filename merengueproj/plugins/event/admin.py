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
        pass


def register(site):
    site.register(Category, EventCategoryAdmin)
    site.register(Event, EventAdmin)
